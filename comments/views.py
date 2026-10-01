from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from posts.models import Post
from posts.access import can_view_post
from .models import Comment
from .serializers import CommentSerializer


def api_response(success, message, data=None, errors=None, http_status=status.HTTP_200_OK):
    return Response({
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
        "meta": {},
    }, status=http_status)


class PostCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_visible_post(self, request, post_id):
        post = Post.objects.filter(id=post_id, status=Post.Status.ACTIVE).select_related("author").first()
        if post is None or not can_view_post(request.user, post):
            return None
        return post

    @extend_schema(responses=CommentSerializer(many=True))
    def get(self, request, post_id):
        post = self.get_visible_post(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post=post).select_related("author")
        serializer = CommentSerializer(comments, many=True)
        return api_response(True, "Comments retrieved successfully.", serializer.data)

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    def post(self, request, post_id):
        post = self.get_visible_post(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(False, "Invalid comment data.", errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save(post=post, author=request.user)
        return api_response(True, "Comment created successfully.", CommentSerializer(comment).data, http_status=status.HTTP_201_CREATED)
