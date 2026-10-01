from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .access import can_view_post
from .models import Post, PostLike, SavedPost, PostShare
from .serializers import PostSerializer, SavedPostSerializer


def api_response(success, message, data=None, errors=None, http_status=status.HTTP_200_OK, meta=None):
    return Response({
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
        "meta": meta or {},
    }, status=http_status)


def get_visible_post_or_none(request, post_id):
    post = Post.objects.filter(id=post_id, status=Post.Status.ACTIVE).select_related("author").first()
    if post is None or not can_view_post(request.user, post):
        return None
    return post


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    @extend_schema(responses=PostSerializer(many=True))
    def get(self, request):
        posts = Post.objects.filter(status=Post.Status.ACTIVE).select_related("author").prefetch_related(
            "media", "likes", "comments", "shares", "saves"
        )
        visible = [post for post in posts if can_view_post(request.user, post)]
        serializer = PostSerializer(visible, many=True, context={"request": request})
        return api_response(True, "Posts retrieved successfully.", serializer.data)

    @extend_schema(request=PostSerializer, responses=PostSerializer)
    def post(self, request):
        serializer = PostSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return api_response(False, "Invalid post data.", errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        post = serializer.save(author=request.user)
        return api_response(True, "Post created successfully.", PostSerializer(post, context={"request": request}).data, http_status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_post(self, post_id):
        return Post.objects.filter(id=post_id, status=Post.Status.ACTIVE).select_related("author").first()

    def get(self, request, post_id):
        post = get_visible_post_or_none(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        return api_response(True, "Post retrieved successfully.", PostSerializer(post, context={"request": request}).data)

    @extend_schema(request=PostSerializer, responses=PostSerializer)
    def patch(self, request, post_id):
        post = self.get_post(post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        if post.author_id != request.user.id:
            return api_response(False, "You can only edit your own posts.", http_status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data, partial=True, context={"request": request})
        if not serializer.is_valid():
            return api_response(False, "Invalid post data.", errors=serializer.errors, http_status=status.HTTP_400_BAD_REQUEST)
        post = serializer.save()
        return api_response(True, "Post updated successfully.", PostSerializer(post, context={"request": request}).data)

    def delete(self, request, post_id):
        post = self.get_post(post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        if post.author_id != request.user.id:
            return api_response(False, "You can only delete your own posts.", http_status=status.HTTP_403_FORBIDDEN)
        post.status = Post.Status.DELETED
        post.save(update_fields=["status", "updated_at"])
        return api_response(True, "Post deleted successfully.")


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_visible_post_or_none(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        try:
            PostLike.objects.create(post=post, user=request.user)
        except IntegrityError:
            return api_response(False, "You have already liked this post.", http_status=status.HTTP_400_BAD_REQUEST)
        return api_response(True, "Post liked successfully.", {"post_id": post.id, "is_liked": True}, http_status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        post = get_visible_post_or_none(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        deleted, _ = PostLike.objects.filter(post=post, user=request.user).delete()
        if not deleted:
            return api_response(False, "You have not liked this post.", http_status=status.HTTP_404_NOT_FOUND)
        return api_response(True, "Post unliked successfully.", {"post_id": post.id, "is_liked": False})


class PostSaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_visible_post_or_none(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        try:
            SavedPost.objects.create(post=post, user=request.user)
        except IntegrityError:
            return api_response(False, "You have already saved this post.", http_status=status.HTTP_400_BAD_REQUEST)
        return api_response(True, "Post saved successfully.", {"post_id": post.id, "is_saved": True}, http_status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        post = get_visible_post_or_none(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        deleted, _ = SavedPost.objects.filter(post=post, user=request.user).delete()
        if not deleted:
            return api_response(False, "This post is not in your saved posts.", http_status=status.HTTP_404_NOT_FOUND)
        return api_response(True, "Post removed from saved posts.", {"post_id": post.id, "is_saved": False})


class SavedPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved = SavedPost.objects.filter(user=request.user, post__status=Post.Status.ACTIVE).select_related(
            "post", "post__author"
        ).prefetch_related("post__media")
        visible = [item for item in saved if can_view_post(request.user, item.post)]
        return api_response(True, "Saved posts retrieved successfully.", SavedPostSerializer(
            visible, many=True, context={"request": request}
        ).data)


class PostShareView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_visible_post_or_none(request, post_id)
        if post is None:
            return api_response(False, "Post not found.", http_status=status.HTTP_404_NOT_FOUND)
        share = PostShare.objects.create(post=post, user=request.user)
        share_url = request.build_absolute_uri(f"/api/v1/posts/{post.id}/")
        return api_response(True, "Post shared successfully.", {
            "share_id": share.id,
            "post_id": post.id,
            "share_url": share_url,
        }, http_status=status.HTTP_201_CREATED)
