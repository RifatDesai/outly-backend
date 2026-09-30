
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import User
from profiles.models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        write_only=True,
        max_length=100,
        trim_whitespace=True,
    )

    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    terms_accepted = serializers.BooleanField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
            "phone",
            "password",
            "confirm_password",
            "terms_accepted",
        ]

    def validate_full_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Full name is required."
            )
        return value.strip()

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        if not attrs["terms_accepted"]:
            raise serializers.ValidationError({
                "terms_accepted": (
                    "You must accept the Terms of Service "
                    "and Privacy Policy."
                )
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        full_name = validated_data.pop("full_name")
        validated_data.pop("confirm_password")
        validated_data.pop("terms_accepted")

        password = validated_data.pop("password")
        email = validated_data.pop("email")
        phone = validated_data.pop("phone", None)

        user = User.objects.create_user(
            email=email,
            password=password,
            phone=phone,
            terms_accepted_at=timezone.now(),
        )

        UserProfile.objects.create(
            user=user,
            username=f"user_{user.id}",
            display_name=full_name,
        )

        return user