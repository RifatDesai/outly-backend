from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(
        source="author.id",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author_id",
            "content",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "post",
            "author_id",
            "created_at",
            "updated_at",
        ]