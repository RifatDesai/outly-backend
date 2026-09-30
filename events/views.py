
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from follows.models import Follow
from .models import Event, EventParticipant
from .serializers import EventSerializer, EventParticipantSerializer


def api_response(success, message, data=None, errors=None, http_status=200):
    return Response(
        {
            "success": success,
            "message": message,
            "data": data,
            "errors": errors,
            "meta": {},
        },
        status=http_status,
    )


def is_event_organizer(user):
    return (
        user.is_authenticated
        and getattr(user, "role", None)
        in ["ORGANIZER", "ADMINISTRATOR"]
    )


def can_view_event(event, user):
    if event.organizer_id == user.id:
        return True

    if event.approval_status != Event.ApprovalStatus.APPROVED:
        return False

    if event.visibility == Event.Visibility.PUBLIC:
        return True

    if event.visibility == Event.Visibility.FOLLOWERS:
        return Follow.objects.filter(
            follower=user,
            following_id=event.organizer_id,
        ).exists()

    if event.visibility == Event.Visibility.INVITED:
        return EventParticipant.objects.filter(
            event=event,
            user=user,
            status__in=[
                EventParticipant.Status.INVITED,
                EventParticipant.Status.PENDING,
                EventParticipant.Status.APPROVED,
            ],
        ).exists()

    return False


class EventModerationSerializer(serializers.Serializer):
    approval_status = serializers.ChoiceField(
        choices=[
            Event.ApprovalStatus.APPROVED,
            Event.ApprovalStatus.REJECTED,
        ]
    )


class EventListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=EventSerializer(many=True))
    def get(self, request):
        events = (
            Event.objects.select_related("organizer", "place", "trail")
            .filter(
                Q(
                    approval_status=Event.ApprovalStatus.APPROVED,
                    visibility=Event.Visibility.PUBLIC,
                )
                | Q(
                    approval_status=Event.ApprovalStatus.APPROVED,
                    visibility=Event.Visibility.FOLLOWERS,
                    organizer__follower_relationships__follower=request.user,
                )
                | Q(organizer=request.user)
                | Q(
                    approval_status=Event.ApprovalStatus.APPROVED,
                    visibility=Event.Visibility.INVITED,
                    participants__user=request.user,
                    participants__status__in=[
                        EventParticipant.Status.INVITED,
                        EventParticipant.Status.PENDING,
                        EventParticipant.Status.APPROVED,
                    ],
                )
            )
            .distinct()
            .order_by("start_at")
        )

        serializer = EventSerializer(events, many=True)
        return api_response(
            True,
            "Events retrieved successfully",
            serializer.data,
        )

    @extend_schema(
        request=EventSerializer,
        responses={201: EventSerializer},
    )
    def post(self, request):
        if not is_event_organizer(request.user):
            return api_response(
                False,
                "Only organizers or administrators can create events",
                http_status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EventSerializer(data=request.data)

        if not serializer.is_valid():
            return api_response(
                False,
                "Invalid event data",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        event = serializer.save(
            organizer=request.user,
            approval_status=Event.ApprovalStatus.PENDING,
        )

        return api_response(
            True,
            "Event created successfully and is pending moderation",
            EventSerializer(event).data,
            http_status=status.HTTP_201_CREATED,
        )


class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=EventSerializer)
    def get(self, request, event_id):
        event = get_object_or_404(
            Event.objects.select_related("organizer", "place", "trail"),
            id=event_id,
        )

        if not can_view_event(event, request.user):
            return api_response(
                False,
                "Event not found",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        return api_response(
            True,
            "Event retrieved successfully",
            EventSerializer(event).data,
        )

    @extend_schema(
        request=EventSerializer,
        responses=EventSerializer,
    )
    def patch(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)

        if (
            event.organizer_id != request.user.id
            and getattr(request.user, "role", None) != "ADMINISTRATOR"
        ):
            return api_response(
                False,
                "You cannot edit this event",
                http_status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EventSerializer(
            event,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return api_response(
                False,
                "Invalid event data",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return api_response(
            True,
            "Event updated successfully",
            EventSerializer(event).data,
        )


class EventModerateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EventModerationSerializer,
        responses={200: EventSerializer},
        description=(
            "Approve or reject a pending event. "
            "Only content moderators and administrators may use this endpoint."
        ),
    )
    def patch(self, request, event_id):
        if getattr(request.user, "role", None) not in [
            "CONTENT_MODERATOR",
            "ADMINISTRATOR",
        ]:
            return api_response(
                False,
                "Only content moderators or administrators can moderate events",
                http_status=status.HTTP_403_FORBIDDEN,
            )

        event = get_object_or_404(Event, id=event_id)

        if event.approval_status != Event.ApprovalStatus.PENDING:
            return api_response(
                False,
                "Only pending events can be moderated",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EventModerationSerializer(data=request.data)

        if not serializer.is_valid():
            return api_response(
                False,
                "Invalid moderation data",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        event.approval_status = serializer.validated_data["approval_status"]
        event.save(update_fields=["approval_status", "updated_at"])

        message = (
            "Event approved successfully"
            if event.approval_status == Event.ApprovalStatus.APPROVED
            else "Event rejected successfully"
        )

        return api_response(
            True,
            message,
            EventSerializer(event).data,
        )


class EventJoinView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={201: EventParticipantSerializer},
    )
    def post(self, request, event_id):
        try:
            with transaction.atomic():
                event = Event.objects.select_for_update().get(id=event_id)

                if not can_view_event(event, request.user):
                    return api_response(
                        False,
                        "Event not found",
                        http_status=status.HTTP_404_NOT_FOUND,
                    )

                if event.organizer_id == request.user.id:
                    return api_response(
                        False,
                        "You cannot register for your own event",
                        http_status=status.HTTP_400_BAD_REQUEST,
                    )

                if event.approval_status != Event.ApprovalStatus.APPROVED:
                    return api_response(
                        False,
                        "This event is not open for registration",
                        http_status=status.HTTP_400_BAD_REQUEST,
                    )

                if event.start_at <= timezone.now():
                    return api_response(
                        False,
                        "Registration is closed because the event has started",
                        http_status=status.HTTP_400_BAD_REQUEST,
                    )

                existing = EventParticipant.objects.filter(
                    event=event,
                    user=request.user,
                ).first()

                if (
                    existing
                    and existing.status != EventParticipant.Status.INVITED
                ):
                    return api_response(
                        False,
                        "You have already registered for this event",
                        http_status=status.HTTP_409_CONFLICT,
                    )

                if (
                    event.visibility == Event.Visibility.INVITED
                    and not existing
                ):
                    return api_response(
                        False,
                        "You must be invited to join this event",
                        http_status=status.HTTP_403_FORBIDDEN,
                    )

                occupied = EventParticipant.objects.filter(
                    event=event,
                    status__in=[
                        EventParticipant.Status.PENDING,
                        EventParticipant.Status.APPROVED,
                    ],
                ).count()

                if occupied >= event.capacity:
                    return api_response(
                        False,
                        "This event has reached its capacity",
                        http_status=status.HTTP_409_CONFLICT,
                    )

                new_status = (
                    EventParticipant.Status.PENDING
                    if event.requires_approval
                    else EventParticipant.Status.APPROVED
                )

                if existing:
                    participant = existing
                    participant.status = new_status
                    participant.save(
                        update_fields=["status", "updated_at"],
                    )
                else:
                    participant = EventParticipant.objects.create(
                        event=event,
                        user=request.user,
                        status=new_status,
                    )

        except Event.DoesNotExist:
            return api_response(
                False,
                "Event not found",
                http_status=status.HTTP_404_NOT_FOUND,
            )
        except IntegrityError:
            return api_response(
                False,
                "You have already registered for this event",
                http_status=status.HTTP_409_CONFLICT,
            )

        message = (
            "Registration request submitted for organizer approval"
            if participant.status == EventParticipant.Status.PENDING
            else "Event registration successful"
        )

        return api_response(
            True,
            message,
            EventParticipantSerializer(participant).data,
            http_status=status.HTTP_201_CREATED,
        )


class EventInviteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID of the user to invite",
            ),
        ],
        responses={201: EventParticipantSerializer},
        description=(
            "Invite a user to an invite-only event. "
            "Supply user_id as a query parameter."
        ),
    )
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)

        if (
            event.organizer_id != request.user.id
            and getattr(request.user, "role", None) != "ADMINISTRATOR"
        ):
            return api_response(
                False,
                "Only the event organizer or an administrator can invite users",
                http_status=status.HTTP_403_FORBIDDEN,
            )

        if event.visibility != Event.Visibility.INVITED:
            return api_response(
                False,
                "Invitations are only supported for invite-only events",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        raw_user_id = request.query_params.get("user_id")

        if not raw_user_id or not raw_user_id.isdigit():
            return api_response(
                False,
                "Provide a valid user_id query parameter",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        invited_user = get_object_or_404(User, id=int(raw_user_id))

        if invited_user.id == event.organizer_id:
            return api_response(
                False,
                "You cannot invite the event organizer",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        participant, created = EventParticipant.objects.get_or_create(
            event=event,
            user=invited_user,
            defaults={"status": EventParticipant.Status.INVITED},
        )

        if not created:
            return api_response(
                False,
                "This user already has a participation record for the event",
                http_status=status.HTTP_409_CONFLICT,
            )

        return api_response(
            True,
            "User invited successfully",
            EventParticipantSerializer(participant).data,
            http_status=status.HTTP_201_CREATED,
        )