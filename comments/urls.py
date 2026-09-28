from django.urls import path

from .views import PostCommentsView


urlpatterns = [
    path(
        "posts/<int:post_id>/comments/",
        PostCommentsView.as_view(),
        name="post-comments"
    ),
]