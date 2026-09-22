from rest_framework import serializers

from .models import Block, Follow


class FollowSerializer(serializers.ModelSerializer):
    follower_id = serializers.IntegerField(
        source="follower.id",
        read_only=True,
    )

    following_id = serializers.IntegerField(
        source="following.id",
        read_only=True,
    )

    class Meta:
        model = Follow
        fields = [
            "id",
            "follower_id",
            "following_id",
            "created_at",
        ]


class BlockSerializer(serializers.ModelSerializer):
    blocker_id = serializers.IntegerField(
        source="blocker.id",
        read_only=True,
    )

    blocked_id = serializers.IntegerField(
        source="blocked.id",
        read_only=True,
    )

    class Meta:
        model = Block
        fields = [
            "id",
            "blocker_id",
            "blocked_id",
            "created_at",
        ]