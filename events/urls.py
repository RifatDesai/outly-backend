
from django.urls import path

from .views import (
    EventListCreateView,
    EventDetailView,
    EventModerateView,
    EventJoinView,
    EventInviteView,
)

urlpatterns = [
    path("", EventListCreateView.as_view(), name="event-list-create"),
    path(
        "<int:event_id>/",
        EventDetailView.as_view(),
        name="event-detail",
    ),
    path(
        "<int:event_id>/moderate/",
        EventModerateView.as_view(),
        name="event-moderate",
    ),
    path(
        "<int:event_id>/join/",
        EventJoinView.as_view(),
        name="event-join",
    ),
    path(
        "<int:event_id>/invite/",
        EventInviteView.as_view(),
        name="event-invite",
    ),
]