from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from posts.models import Post
from .models import Comment
from .serializers import CommentSerializer


class PostCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=CommentSerializer(many=True),
    )
    def get(self, request, post_id):
        try:
            post = Post.objects.get(
                id=post_id,
                status=Post.Status.ACTIVE
            )
        except Post.DoesNotExist:
            return Response({
                "success": False,
                "message": "Post not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(
            post=post
        ).select_related("author")

        serializer = CommentSerializer(comments, many=True)

        return Response({
            "success": True,
            "message": "Comments retrieved successfully",
            "data": serializer.data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=CommentSerializer,
        responses=CommentSerializer,
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(
                id=post_id,
                status=Post.Status.ACTIVE
            )
        except Post.DoesNotExist:
            return Response({
                "success": False,
                "message": "Post not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(
                post=post,
                author=request.user
            )

            return Response({
                "success": True,
                "message": "Comment created successfully",
                "data": CommentSerializer(comment).data,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid comment data",
            "data": None,
            "errors": serializer.errors,
            "meta": {}
        }, status=status.HTTP_400_BAD_REQUEST)
