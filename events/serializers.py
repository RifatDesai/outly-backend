
from django.utils import timezone
from rest_framework import serializers

from .models import Event, EventParticipant
from places.models import Place
from trails.models import Trail


class EventSerializer(serializers.ModelSerializer):
    organizer_id = serializers.IntegerField(
        source="organizer.id",
        read_only=True
    )

    place_id = serializers.PrimaryKeyRelatedField(
        source="place",
        queryset=Place.objects.all(),
        required=False,
        allow_null=True
    )

    trail_id = serializers.PrimaryKeyRelatedField(
        source="trail",
        queryset=Trail.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "organizer_id",
            "title",
            "description",
            "category",
            "place_id",
            "trail_id",
            "location",
            "meeting_point",
            "start_at",
            "end_at",
            "capacity",
            "difficulty",
            "requires_approval",
            "visibility",
            "approval_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organizer_id",
            "approval_status",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Title is required."
            )
        return value.strip()

    def validate_location(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Location is required."
            )
        return value.strip()

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Capacity must be at least 1."
            )
        return value

    def validate(self, attrs):
        start_at = attrs.get(
            "start_at",
            getattr(self.instance, "start_at", None)
        )
        end_at = attrs.get(
            "end_at",
            getattr(self.instance, "end_at", None)
        )

        if self.instance is None and not start_at:
            raise serializers.ValidationError({
                "start_at": "Start date and time are required."
            })

        if start_at and start_at <= timezone.now():
            if self.instance is None:
                raise serializers.ValidationError({
                    "start_at": "Start date and time must be in the future."
                })

        if start_at and end_at and end_at < start_at:
            raise serializers.ValidationError({
                "end_at": "End time cannot be before start time."
            })

        if end_at and start_at and end_at == start_at:
            raise serializers.ValidationError({
                "end_at": "End time must be after start time."
            })

        if (
            attrs.get("place") is not None
            and attrs.get("trail") is not None
        ):
            raise serializers.ValidationError(
                "Link either a place or a trail, not both."
            )

        return attrs


class EventParticipantSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    event_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = EventParticipant
        fields = [
            "id",
            "event_id",
            "user_id",
            "status",
            "joined_at",
            "updated_at",
        ]
        read_only_fields = fields