
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from accounts.models import User
from follows.models import Block

from .models import UserProfile
from .serializers import (
    MyProfileSerializer,
    PublicProfileSerializer,
)


def get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "username": f"user_{user.id}",
        },
    )
    return profile


def api_response(success, message, data=None, errors=None,
                 http_status=status.HTTP_200_OK):
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


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=MyProfileSerializer)
    def get(self, request):
        profile = get_user_profile(request.user)
        serializer = MyProfileSerializer(profile)

        return api_response(
            True,
            "Profile fetched successfully.",
            serializer.data,
        )

    @extend_schema(
        request=MyProfileSerializer,
        responses=MyProfileSerializer,
    )
    def patch(self, request):
        profile = get_user_profile(request.user)

        serializer = MyProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return api_response(
                False,
                "Profile update failed.",
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return api_response(
            True,
            "Profile updated successfully.",
            serializer.data,
        )


class PublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PublicProfileSerializer)
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # Users cannot view each other's profiles
        # when either person has blocked the other.
        if request.user.id != user.id:
            blocked = Block.objects.filter(
                blocker=request.user,
                blocked=user,
            ).exists()

            blocked_by_user = Block.objects.filter(
                blocker=user,
                blocked=request.user,
            ).exists()

            if blocked or blocked_by_user:
                return api_response(
                    False,
                    "Profile not found.",
                    http_status=status.HTTP_404_NOT_FOUND,
                )

        profile = get_user_profile(user)

        # The owner can still view their own profile.
        if request.user.id != user.id:
            visibility = (
                profile.privacy_settings or {}
            ).get("profile_visibility", "public")

            if visibility == "private":
                return api_response(
                    False,
                    "This profile is private.",
                    http_status=status.HTTP_403_FORBIDDEN,
                )

        serializer = PublicProfileSerializer(profile)

        return api_response(
            True,
            "User profile fetched successfully.",
            serializer.data,
        )