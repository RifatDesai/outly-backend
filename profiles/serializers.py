
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

    privacy_settings = serializers.JSONField(required=False)

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

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username cannot be empty."
            )

        existing_profiles = UserProfile.objects.filter(
            username__iexact=value
        )

        if self.instance:
            existing_profiles = existing_profiles.exclude(
                pk=self.instance.pk
            )

        if existing_profiles.exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    def validate_interests(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Interests must be a list."
            )

        if not all(
            isinstance(item, str) and item.strip()
            for item in value
        ):
            raise serializers.ValidationError(
                "Each interest must be a non-empty string."
            )

        return [item.strip() for item in value]

    def validate_privacy_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Privacy settings must be a JSON object."
            )

        visibility = value.get("profile_visibility")

        if visibility is not None and visibility not in [
            "public",
            "private",
        ]:
            raise serializers.ValidationError(
                "profile_visibility must be 'public' or 'private'."
            )

        return value


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