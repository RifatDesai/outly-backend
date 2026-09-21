from rest_framework import serializers

from .models import UserProfile


class MyProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    role = serializers.CharField(
        source="user.role",
        read_only=True,
    )

    status = serializers.CharField(
        source="user.status",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "user_id",
            "email",
            "role",
            "status",
            "username",
            "display_name",
            "photo",
            "bio",
            "interests",
            "privacy_settings",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "user_id",
            "email",
            "role",
            "status",
            "created_at",
            "updated_at",
        ]


class PublicProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "user_id",
            "username",
            "display_name",
            "photo",
            "bio",
            "interests",
        ]