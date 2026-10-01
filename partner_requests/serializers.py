from rest_framework import serializers
from .models import PartnerRequest, PartnerRequestJoin

class PartnerRequestSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    owner_name = serializers.SerializerMethodField()
    spots_filled = serializers.IntegerField(read_only=True)

    class Meta:
        model = PartnerRequest
        fields = ["id", "owner_id", "owner_name", "activity", "destination", "preferred_datetime",
                  "spots_total", "spots_filled", "experience_level", "description", "visibility",
                  "status", "created_at", "updated_at"]
        read_only_fields = ["id", "owner_id", "owner_name", "spots_filled", "status", "created_at", "updated_at"]

    def get_owner_name(self, obj):
        profile = getattr(obj.owner, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.owner.email

    def validate_spots_total(self, value):
        if value < 1:
            raise serializers.ValidationError("At least one spot is required.")
        return value

class PartnerRequestJoinSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = PartnerRequestJoin
        fields = ["id", "request", "user_id", "user_name", "status", "message", "created_at", "updated_at"]
        read_only_fields = ["id", "request", "user_id", "user_name", "status", "created_at", "updated_at"]

    def get_user_name(self, obj):
        profile = getattr(obj.user, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.user.email
