
from django.db.models import Q

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Activity, ActivityParticipant
from .serializers import ActivitySerializer, ActivityParticipantSerializer
from follows.models import Follow


class ActivityListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ActivitySerializer(many=True),
    )
    def get(self, request):
        activities = Activity.objects.filter(
            Q(privacy="PUBLIC")
            | Q(created_by=request.user)
            | Q(
                privacy="FOLLOWERS",
                created_by__follower_relationships__follower=request.user,
            )
        ).select_related("created_by").distinct()

        serializer = ActivitySerializer(activities, many=True)

        return Response({
            "success": True,
            "message": "Activities retrieved successfully",
            "data": serializer.data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=ActivitySerializer,
        responses=ActivitySerializer,
    )
    def post(self, request):
        serializer = ActivitySerializer(data=request.data)

        if serializer.is_valid():
            activity = serializer.save(created_by=request.user)

            return Response({
                "success": True,
                "message": "Activity created successfully",
                "data": ActivitySerializer(activity).data,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid activity data",
            "data": None,
            "errors": serializer.errors,
            "meta": {}
        }, status=status.HTTP_400_BAD_REQUEST)


class ActivityDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_activity(self, activity_id):
        try:
            return Activity.objects.select_related(
                "created_by"
            ).get(id=activity_id)
        except Activity.DoesNotExist:
            return None

    def activity_is_visible(self, activity, user):
        if activity.created_by_id == user.id:
            return True

        if activity.privacy == "PUBLIC":
            return True

        if activity.privacy == "FOLLOWERS":
            return Follow.objects.filter(
                follower=user,
                following_id=activity.created_by_id,
            ).exists()

        return False

    @extend_schema(
        responses=ActivitySerializer,
    )
    def get(self, request, activity_id):
        activity = self.get_activity(activity_id)

        if activity is None or not self.activity_is_visible(
            activity, request.user
        ):
            return Response({
                "success": False,
                "message": "Activity not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ActivitySerializer(activity)

        return Response({
            "success": True,
            "message": "Activity retrieved successfully",
            "data": serializer.data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=ActivitySerializer,
        responses=ActivitySerializer,
    )
    def patch(self, request, activity_id):
        activity = self.get_activity(activity_id)

        if activity is None:
            return Response({
                "success": False,
                "message": "Activity not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        if activity.created_by_id != request.user.id:
            return Response({
                "success": False,
                "message": "You can only edit your own activities",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = ActivitySerializer(
            activity,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            activity = serializer.save()

            return Response({
                "success": True,
                "message": "Activity updated successfully",
                "data": ActivitySerializer(activity).data,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Invalid activity data",
            "data": None,
            "errors": serializer.errors,
            "meta": {}
        }, status=status.HTTP_400_BAD_REQUEST)


class ActivityJoinView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={201: ActivityParticipantSerializer},
        description="Join an activity that the authenticated user can access."
    )
    def post(self, request, activity_id):
        try:
            activity = Activity.objects.select_related(
                "created_by"
            ).get(id=activity_id)
        except Activity.DoesNotExist:
            return Response({
                "success": False,
                "message": "Activity not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Reuse the existing privacy rules.
        detail_view = ActivityDetailView()
        if not detail_view.activity_is_visible(activity, request.user):
            return Response({
                "success": False,
                "message": "Activity not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        if activity.created_by_id == request.user.id:
            return Response({
                "success": False,
                "message": "You cannot join your own activity",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        if activity.status == Activity.Status.COMPLETED:
            return Response({
                "success": False,
                "message": "You cannot join a completed activity",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        participant, created = ActivityParticipant.objects.get_or_create(
            activity=activity,
            user=request.user
        )

        if not created:
            return Response({
                "success": False,
                "message": "You have already joined this activity",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_409_CONFLICT)

        return Response({
            "success": True,
            "message": "Activity joined successfully",
            "data": ActivityParticipantSerializer(participant).data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_201_CREATED)