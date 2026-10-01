from django.urls import path
from .views import (
    PartnerRequestListCreateView, PartnerRequestDetailView, PartnerRequestJoinView,
    PartnerRequestJoinRequestsView, PartnerRequestCloseView,
)

urlpatterns = [
    path("", PartnerRequestListCreateView.as_view(), name="partner-request-list-create"),
    path("<int:request_id>/", PartnerRequestDetailView.as_view(), name="partner-request-detail"),
    path("<int:request_id>/join/", PartnerRequestJoinView.as_view(), name="partner-request-join"),
    path("<int:request_id>/join-requests/", PartnerRequestJoinRequestsView.as_view(), name="partner-request-join-requests"),
    path("<int:request_id>/join-requests/<int:join_id>/review/", PartnerRequestJoinRequestsView.as_view(), name="partner-request-review"),
    path("<int:request_id>/close/", PartnerRequestCloseView.as_view(), name="partner-request-close"),
]
