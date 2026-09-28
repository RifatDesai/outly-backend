from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Post
from .serializers import PostSerializer


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses=PostSerializer(many=True),
    )
    def get(self, request):
        posts = Post.objects.filter(
            status=Post.Status.ACTIVE
        ).select_related("author")

        serializer = PostSerializer(posts, many=True)

        return Response({
            "success": True,
            "message": "Posts retrieved successfully",
            "data": serializer.data,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=PostSerializer,
        responses=PostSerializer,
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            post = serializer.save(author=request.user)

            return Response({
                "success": True,
                "message": "Post created successfully",
                "data": PostSerializer(post).data,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid post data",
            "data": None,
            "errors": serializer.errors,
            "meta": {}
        }, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        try:
            return Post.objects.get(
                id=post_id,
                status=Post.Status.ACTIVE
            )
        except Post.DoesNotExist:
            return None

    @extend_schema(
        request=PostSerializer,
        responses=PostSerializer,
    )
    def patch(self, request, post_id):
        post = self.get_post(post_id)

        if post is None:
            return Response({
                "success": False,
                "message": "Post not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response({
                "success": False,
                "message": "You can only edit your own posts",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(
            post,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            post = serializer.save()

            return Response({
                "success": True,
                "message": "Post updated successfully",
                "data": PostSerializer(post).data,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Invalid post data",
            "data": None,
            "errors": serializer.errors,
            "meta": {}
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = self.get_post(post_id)

        if post is None:
            return Response({
                "success": False,
                "message": "Post not found",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response({
                "success": False,
                "message": "You can only delete your own posts",
                "data": None,
                "errors": None,
                "meta": {}
            }, status=status.HTTP_403_FORBIDDEN)

        post.status = Post.Status.DELETED
        post.save(update_fields=["status", "updated_at"])

        return Response({
            "success": True,
            "message": "Post deleted successfully",
            "data": None,
            "errors": None,
            "meta": {}
        }, status=status.HTTP_200_OK)