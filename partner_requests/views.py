
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from .models import PartnerRequest, PartnerRequestJoin
from .serializers import PartnerRequestSerializer, PartnerRequestJoinSerializer


def ok(data, message="Success", code=200):
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
            "errors": None,
            "meta": {},
        },
        status=code,
    )


def fail(message, code=400, errors=None):
    return Response(
        {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors or {},
            "meta": {},
        },
        status=code,
    )


class PartnerRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PartnerRequestSerializer(many=True))
    def get(self, request):
        qs = (
            PartnerRequest.objects.filter(status="OPEN", visibility="PUBLIC")
            | PartnerRequest.objects.filter(owner=request.user)
        )
        return ok(
            PartnerRequestSerializer(
                qs.distinct().select_related("owner", "owner__profile"),
                many=True,
            ).data
        )

    @extend_schema(
        request=PartnerRequestSerializer,
        responses={201: PartnerRequestSerializer},
    )
    def post(self, request):
        serializer = PartnerRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return fail(
                "Please correct the partner request details.",
                400,
                serializer.errors,
            )

        if serializer.validated_data["preferred_datetime"] < timezone.now():
            return fail(
                "Preferred date and time must be in the future.",
                400,
                {
                    "preferred_datetime": [
                        "Choose a future date and time."
                    ]
                },
            )

        item = serializer.save(owner=request.user)
        return ok(
            PartnerRequestSerializer(item).data,
            "Partner request created.",
            201,
        )


class PartnerRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, request_id):
        item = get_object_or_404(PartnerRequest, pk=request_id)

        if item.visibility == "PRIVATE" and item.owner_id != request.user.id:
            join = item.join_requests.filter(
                user=request.user,
                status="ACCEPTED",
            ).exists()

            if not join:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("This partner request is private.")

        return item

    def get(self, request, request_id):
        item = self.get_object(request, request_id)
        return ok(PartnerRequestSerializer(item).data)

    @extend_schema(
        request=PartnerRequestSerializer,
        responses=PartnerRequestSerializer,
    )
    def patch(self, request, request_id):
        item = get_object_or_404(PartnerRequest, pk=request_id)

        if item.owner_id != request.user.id:
            return fail("Only the request owner can edit it.", 403)

        if item.status != "OPEN":
            return fail("Closed requests cannot be edited.", 400)

        serializer = PartnerRequestSerializer(
            item,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return fail(
                "Please correct the partner request details.",
                400,
                serializer.errors,
            )

        dt = serializer.validated_data.get(
            "preferred_datetime",
            item.preferred_datetime,
        )

        if dt < timezone.now():
            return fail(
                "Preferred date and time must be in the future.",
                400,
                {
                    "preferred_datetime": [
                        "Choose a future date and time."
                    ]
                },
            )

        if (
            serializer.validated_data.get("spots_total", item.spots_total)
            < item.spots_filled
        ):
            return fail(
                "Total spots cannot be less than the number already filled.",
                400,
            )

        serializer.save()
        return ok(
            PartnerRequestSerializer(item).data,
            "Partner request updated.",
        )

    def delete(self, request, request_id):
        item = get_object_or_404(PartnerRequest, pk=request_id)

        if item.owner_id != request.user.id:
            return fail("Only the request owner can delete it.", 403)

        item.delete()
        return ok({}, "Partner request deleted.")


class PartnerRequestJoinView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="PartnerJoinRequestInput",
            fields={
                "message": serializers.CharField(
                    required=False,
                    allow_blank=True,
                    max_length=500,
                )
            },
        ),
        responses={201: PartnerRequestJoinSerializer},
    )
    def post(self, request, request_id):
        item = get_object_or_404(
            PartnerRequest,
            pk=request_id,
            status="OPEN",
        )

        if item.owner_id == request.user.id:
            return fail(
                "You cannot request to join your own partner request.",
                400,
            )

        if item.visibility == "PRIVATE":
            return fail("This request is private.", 403)

        if item.spots_filled >= item.spots_total:
            return fail("This partner request is full.", 409)

        message = request.data.get("message", "")

        if not isinstance(message, str) or len(message) > 500:
            return fail(
                "message must be 500 characters or fewer.",
                400,
            )

        join, created = PartnerRequestJoin.objects.get_or_create(
            request=item,
            user=request.user,
            defaults={
                "message": message,
                "status": "PENDING",
            },
        )

        if not created:
            if join.status == "PENDING":
                return fail("You have already requested to join.", 409)

            if join.status == "ACCEPTED":
                return fail(
                    "You are already accepted for this request.",
                    409,
                )

            join.status = "PENDING"
            join.message = message
            join.save(
                update_fields=["status", "message", "updated_at"]
            )

        try:
            from notifications.utils import create_notification

            create_notification(
                item.owner,
                "PARTNER_JOIN",
                "New partner request",
                f"{request.user.email} requested to join {item.destination}.",
                actor=request.user,
                target_type="partner_request",
                target_id=item.id,
            )
        except Exception:
            pass

        return ok(
            PartnerRequestJoinSerializer(join).data,
            "Join request sent.",
            201,
        )


class PartnerRequestJoinRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        item = get_object_or_404(PartnerRequest, pk=request_id)

        if item.owner_id != request.user.id:
            return fail(
                "Only the request owner can view join requests.",
                403,
            )

        qs = item.join_requests.select_related("user", "user__profile")
        return ok(PartnerRequestJoinSerializer(qs, many=True).data)

    @extend_schema(
        request=inline_serializer(
            name="PartnerRequestJoinReviewRequest",
            fields={
                "decision": serializers.ChoiceField(
                    choices=["ACCEPTED", "REJECTED"]
                )
            },
        )
    )
    def post(self, request, request_id, join_id):
        item = get_object_or_404(PartnerRequest, pk=request_id)

        if item.owner_id != request.user.id:
            return fail(
                "Only the request owner can review join requests.",
                403,
            )

        join = get_object_or_404(
            PartnerRequestJoin,
            pk=join_id,
            request=item,
            status="PENDING",
        )

        decision = request.data.get("decision")

        if decision not in ["ACCEPTED", "REJECTED"]:
            return fail(
                "decision must be ACCEPTED or REJECTED.",
                400,
            )

        if decision == "ACCEPTED" and item.spots_filled >= item.spots_total:
            return fail("This partner request is full.", 409)

        join.status = decision
        join.save(update_fields=["status", "updated_at"])

        if decision == "ACCEPTED" and item.spots_filled >= item.spots_total:
            item.status = "CLOSED"
            item.save(update_fields=["status", "updated_at"])

        try:
            from notifications.utils import create_notification

            create_notification(
                join.user,
                "PARTNER_REQUEST",
                f"Partner request {decision.lower()}",
                f"Your request to join {item.destination} was {decision.lower()}.",
                actor=request.user,
                target_type="partner_request",
                target_id=item.id,
            )
        except Exception:
            pass

        return ok(
            PartnerRequestJoinSerializer(join).data,
            f"Join request {decision.lower()}.",
        )


class PartnerRequestCloseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        item = get_object_or_404(PartnerRequest, pk=request_id)

        if item.owner_id != request.user.id:
            return fail("Only the request owner can close it.", 403)

        item.status = "CLOSED"
        item.save(update_fields=["status", "updated_at"])

        return ok(
            PartnerRequestSerializer(item).data,
            "Partner request closed.",
        )