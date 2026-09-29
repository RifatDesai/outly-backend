from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    created_by_id = serializers.IntegerField(
        source="created_by.id",
        read_only=True
    )

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "activity_type",
            "description",
            "created_by_id",
            "place_id",
            "trail_id",
            "location",
            "start_at",
            "end_at",
            "distance",
            "duration",
            "difficulty",
            "notes",
            "privacy",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by_id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_at = attrs.get("start_at")
        end_at = attrs.get("end_at")

        if start_at and end_at and end_at < start_at:
            raise serializers.ValidationError(
                "End time cannot be before start time."
            )

        return attrs