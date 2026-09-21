from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from accounts.models import User

from .models import UserProfile
from .serializers import (
    MyProfileSerializer,
    PublicProfileSerializer,
)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MyProfileSerializer,
    )
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "username": f"user_{request.user.id}",
            },
        )

        serializer = MyProfileSerializer(profile)

        return Response(
            {
                "success": True,
                "message": "Profile fetched successfully.",
                "data": serializer.data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=MyProfileSerializer,
        responses=MyProfileSerializer,
    )
    def patch(self, request):
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "username": f"user_{request.user.id}",
            },
        )

        serializer = MyProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Profile update failed.",
                    "data": None,
                    "errors": serializer.errors,
                    "meta": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": serializer.data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )


class PublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=PublicProfileSerializer,
    )
    def get(self, request, user_id):
        user = get_object_or_404(
            User,
            id=user_id,
        )

        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "username": f"user_{user.id}",
            },
        )

        serializer = PublicProfileSerializer(profile)

        return Response(
            {
                "success": True,
                "message": "User profile fetched successfully.",
                "data": serializer.data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )