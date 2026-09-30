from django.urls import path

from .views import ActivityListCreateView, ActivityDetailView, ActivityJoinView


urlpatterns = [
    path(
        "activities/",
        ActivityListCreateView.as_view(),
        name="activities-list-create",
    ),
    path(
        "activities/<int:activity_id>/",
        ActivityDetailView.as_view(),
        name="activity-detail",
    ),
    path(
    "<int:activity_id>/join/",
    ActivityJoinView.as_view(),
    name="activity-join"
    ),
]