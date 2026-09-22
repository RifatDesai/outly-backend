from django.urls import path

from .views import FollowUserView, BlockUserView


urlpatterns = [
    path(
        "users/<int:user_id>/follow/",
        FollowUserView.as_view(),
        name="follow-user",
    ),
    path(
        "users/<int:user_id>/block/",
        BlockUserView.as_view(),
        name="block-user",
    ),
]