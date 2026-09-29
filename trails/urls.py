from django.urls import path
from .views import TrailListCreateView, TrailDetailView, TrailPointsView

urlpatterns = [
    path("trails/", TrailListCreateView.as_view(), name="trails-list-create"),
    path("trails/<int:trail_id>/", TrailDetailView.as_view(), name="trail-detail"),
    path(
    "trails/<int:trail_id>/points/",
    TrailPointsView.as_view(),
    name="trail-points",
),
]