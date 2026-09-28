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
            "name",
            "description",
            "created_by_id",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by_id",
            "created_at",
            "updated_at",
        ]