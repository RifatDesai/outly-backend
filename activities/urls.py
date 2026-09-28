from django.urls import path

from .views import ActivityListCreateView, ActivityDetailView


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
]