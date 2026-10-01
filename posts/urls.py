from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, PostLikeView, PostSaveView,
    SavedPostsView, PostShareView,
)

urlpatterns = [
    path("posts/", PostListCreateView.as_view(), name="posts-list-create"),
    path("posts/saved/", SavedPostsView.as_view(), name="saved-posts"),
    path("posts/<int:post_id>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/like/", PostLikeView.as_view(), name="post-like"),
    path("posts/<int:post_id>/save/", PostSaveView.as_view(), name="post-save"),
    path("posts/<int:post_id>/share/", PostShareView.as_view(), name="post-share"),
]
