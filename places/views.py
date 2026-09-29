from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Place
from .serializers import PlaceSerializer


class PlaceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PlaceSerializer(many=True))
    def get(self, request):
        places = Place.objects.all()
        serializer = PlaceSerializer(places, many=True)

        return Response(
            {
                "success": True,
                "message": "Places retrieved successfully",
                "data": serializer.data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=PlaceSerializer, responses=PlaceSerializer)
    def post(self, request):
        serializer = PlaceSerializer(data=request.data)

        if serializer.is_valid():
            place = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Place created successfully",
                    "data": PlaceSerializer(place).data,
                    "errors": None,
                    "meta": {},
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid place data",
                "data": None,
                "errors": serializer.errors,
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PlaceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_place(self, place_id):
        try:
            return Place.objects.get(id=place_id)
        except Place.DoesNotExist:
            return None

    @extend_schema(responses=PlaceSerializer)
    def get(self, request, place_id):
        place = self.get_place(place_id)

        if place is None:
            return Response(
                {
                    "success": False,
                    "message": "Place not found",
                    "data": None,
                    "errors": None,
                    "meta": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PlaceSerializer(place)

        return Response(
            {
                "success": True,
                "message": "Place retrieved successfully",
                "data": serializer.data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )