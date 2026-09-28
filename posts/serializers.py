from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):

    author_id = serializers.IntegerField(
        source="author.id",
        read_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "author_id",
            "caption",
            "visibility",
            "activity_id",
            "place_id",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "author_id",
            "status",
            "created_at",
            "updated_at",
        ]