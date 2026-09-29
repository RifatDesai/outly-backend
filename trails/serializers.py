from rest_framework import serializers
from .models import Trail, TrailPoint


class TrailPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrailPoint
        fields = [
            "id",
            "latitude",
            "longitude",
            "sequence",
        ]
        read_only_fields = ["id"]


class TrailSerializer(serializers.ModelSerializer):
    points = TrailPointSerializer(many=True, read_only=True)

    class Meta:
        model = Trail
        fields = [
            "id",
            "name",
            "description",
            "location",
            "difficulty",
            "distance",
            "estimated_duration",
            "facilities",
            "safety_notes",
            "images",
            "rating",
            "is_verified",
            "points",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "points",
            "created_at",
            "updated_at",
        ]