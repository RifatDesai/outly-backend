from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Trail, TrailPoint

from .models import Trail
from .serializers import TrailSerializer, TrailPointSerializer


class TrailListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=TrailSerializer(many=True),
    )
    def get(self, request):
        trails = Trail.objects.all()

        serializer = TrailSerializer(trails, many=True)

        return Response({
            "success": True,
            "message": "Trails retrieved successfully",
            "data": serializer.data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=TrailSerializer,
        responses=TrailSerializer,
    )
    def post(self, request):
        serializer = TrailSerializer(data=request.data)

        if serializer.is_valid():
            trail = serializer.save()

            return Response({
                "success": True,
                "message": "Trail created successfully",
                "data": TrailSerializer(trail).data,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid trail data",
            "data": None,
            "errors": serializer.errors,
            "meta": {}
        }, status=status.HTTP_400_BAD_REQUEST)


class TrailDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_trail(self, trail_id):
        try:
            return Trail.objects.get(id=trail_id)
        except Trail.DoesNotExist:
            return None

    @extend_schema(
        responses=TrailSerializer,
    )
    def get(self, request, trail_id):
        trail = self.get_trail(trail_id)

        if trail is None:
            return Response({
                "success": False,
                "message": "Trail not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TrailSerializer(trail)

        return Response({
            "success": True,
            "message": "Trail retrieved successfully",
            "data": serializer.data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)

class TrailPointsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=TrailPointSerializer(many=True),
    )
    def get(self, request, trail_id):
        try:
            trail = Trail.objects.get(id=trail_id)
        except Trail.DoesNotExist:
            return Response({
                "success": False,
                "message": "Trail not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        points = TrailPoint.objects.filter(trail=trail)

        serializer = TrailPointSerializer(points, many=True)

        return Response({
            "success": True,
            "message": "Trail points retrieved successfully",
            "data": serializer.data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=TrailPointSerializer,
        responses=TrailPointSerializer,
    )
    def post(self, request, trail_id):
        try:
            trail = Trail.objects.get(id=trail_id)
        except Trail.DoesNotExist:
            return Response({
                "success": False,
                "message": "Trail not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TrailPointSerializer(data=request.data)

        if serializer.is_valid():
            point = serializer.save(trail=trail)

            return Response({
                "success": True,
                "message": "Trail point created successfully",
                "data": TrailPointSerializer(point).data,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid trail point data",
            "data": None,
            "errors": serializer.errors,
            "meta": {}
        }, status=status.HTTP_400_BAD_REQUEST)