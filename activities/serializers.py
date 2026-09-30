from rest_framework import serializers

from .models import Activity
from places.models import Place
from trails.models import Trail


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

    def validate_place_id(self, value):
        if value is not None and not Place.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Place with this ID does not exist."
            )
        return value

    def validate_trail_id(self, value):
        if value is not None and not Trail.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Trail with this ID does not exist."
            )
        return value

    def validate(self, attrs):
        # Require location and start time when creating an activity
        if self.instance is None:
            location = attrs.get("location")
            start_at = attrs.get("start_at")

            if not location or not location.strip():
                raise serializers.ValidationError({
                    "location": "Location is required."
                })

            if not start_at:
                raise serializers.ValidationError({
                    "start_at": "Start date and time are required."
                })

        # Check start and end times during creation and updates
        start_at = attrs.get(
            "start_at",
            getattr(self.instance, "start_at", None)
        )
        end_at = attrs.get(
            "end_at",
            getattr(self.instance, "end_at", None)
        )

        if start_at and end_at and end_at < start_at:
            raise serializers.ValidationError({
                "end_at": "End time cannot be before start time."
            })

        return attrs