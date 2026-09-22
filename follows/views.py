from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Block, Follow
from .serializers import BlockSerializer, FollowSerializer


User = get_user_model()


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=FollowSerializer,
    )
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        if target_user == request.user:
            return Response(
                {
                    "success": False,
                    "message": "You cannot follow yourself.",
                    "data": None,
                    "errors": {
                        "user": ["You cannot follow yourself."]
                    },
                    "meta": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Block.objects.filter(
            blocker=target_user,
            blocked=request.user,
        ).exists():
            return Response(
                {
                    "success": False,
                    "message": "You cannot follow this user.",
                    "data": None,
                    "errors": {
                        "user": [
                            "This user has blocked you."
                        ]
                    },
                    "meta": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Block.objects.filter(
            blocker=request.user,
            blocked=target_user,
        ).exists():
            return Response(
                {
                    "success": False,
                    "message": "You have blocked this user.",
                    "data": None,
                    "errors": {
                        "user": [
                            "You cannot follow a user you blocked."
                        ]
                    },
                    "meta": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user,
        )

        if not created:
            return Response(
                {
                    "success": False,
                    "message": "You already follow this user.",
                    "data": FollowSerializer(follow).data,
                    "errors": {
                        "follow": [
                            "Follow relationship already exists."
                        ]
                    },
                    "meta": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "User followed successfully.",
                "data": FollowSerializer(follow).data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        responses={
            200: FollowSerializer,
            404: {"description": "Follow relationship not found"},
        }
    )
    def delete(self, request, user_id):
        target_user = get_object_or_404(
            User,
            id=user_id,
        )

        follow = Follow.objects.filter(
            follower=request.user,
            following=target_user,
        ).first()

        if follow is None:
            return Response(
                {
                    "success": False,
                    "message": "Follow relationship not found.",
                    "data": None,
                    "errors": {
                        "follow": [
                            "You are not following this user."
                        ]
                    },
                    "meta": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        FollowSerializer(follow)

        follow_data = FollowSerializer(follow).data
        follow.delete()

        return Response(
            {
                "success": True,
                "message": "User unfollowed successfully.",
                "data": follow_data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=BlockSerializer,
    )
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        if target_user == request.user:
            return Response(
                {
                    "success": False,
                    "message": "You cannot block yourself.",
                    "data": None,
                    "errors": {
                        "user": ["You cannot block yourself."]
                    },
                    "meta": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        block, created = Block.objects.get_or_create(
            blocker=request.user,
            blocked=target_user,
        )

        if not created:
            return Response(
                {
                    "success": False,
                    "message": "You already blocked this user.",
                    "data": BlockSerializer(block).data,
                    "errors": {
                        "block": [
                            "Block relationship already exists."
                        ]
                    },
                    "meta": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Blocking removes an existing follow in either direction.
        Follow.objects.filter(
            follower=request.user,
            following=target_user,
        ).delete()

        Follow.objects.filter(
            follower=target_user,
            following=request.user,
        ).delete()

        return Response(
            {
                "success": True,
                "message": "User blocked successfully.",
                "data": BlockSerializer(block).data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        responses=BlockSerializer,
    )
    def delete(self, request, user_id):
        target_user = get_object_or_404(
            User,
            id=user_id,
        )

        block = Block.objects.filter(
            blocker=request.user,
            blocked=target_user,
        ).first()

        if block is None:
            return Response(
                {
                    "success": False,
                    "message": "Block relationship not found.",
                    "data": None,
                    "errors": {
                        "block": [
                            "You have not blocked this user."
                        ]
                    },
                    "meta": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        block_data = BlockSerializer(block).data
        block.delete()

        return Response(
            {
                "success": True,
                "message": "User unblocked successfully.",
                "data": block_data,
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )