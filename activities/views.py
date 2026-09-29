from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Activity
from .serializers import ActivitySerializer


class ActivityListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ActivitySerializer(many=True),
    )
    def get(self, request):
        activities = Activity.objects.all().select_related("created_by")

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
            return Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return None

    @extend_schema(
        responses=ActivitySerializer,
    )
    def get(self, request, activity_id):
        activity = self.get_activity(activity_id)

        if activity is None:
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

        if activity.created_by != request.user:
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