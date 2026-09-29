from rest_framework import serializers
from .models import Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "description",
            "coordinates",
            "category",
            "difficulty",
            "distance",
            "estimated_duration",
            "facilities",
            "safety_notes",
            "images",
            "rating",
            "is_verified",
        ]
        read_only_fields = ["id"]