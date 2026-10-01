from django.urls import path
from .views import (
    GroupListCreateView, GroupDetailView, GroupJoinLeaveView, GroupMembersView,
    GroupMemberActionView, GroupFeedView, GroupJoinRequestsView, GroupChatEntryView,
)

urlpatterns = [
    path("", GroupListCreateView.as_view(), name="group-list-create"),
    path("<int:group_id>/", GroupDetailView.as_view(), name="group-detail"),
    path("<int:group_id>/join/", GroupJoinLeaveView.as_view(), name="group-join-leave"),
    path("<int:group_id>/members/", GroupMembersView.as_view(), name="group-members"),
    path("<int:group_id>/members/<int:user_id>/", GroupMemberActionView.as_view(), name="group-member-remove"),
    path("<int:group_id>/members/<int:user_id>/role/", GroupMemberActionView.as_view(), name="group-member-role"),
    path("<int:group_id>/feed/", GroupFeedView.as_view(), name="group-feed"),
    path("<int:group_id>/join-requests/", GroupJoinRequestsView.as_view(), name="group-join-requests"),
    path("<int:group_id>/join-requests/<int:request_id>/review/", GroupJoinRequestsView.as_view(), name="group-join-request-review"),
    path("<int:group_id>/chat/", GroupChatEntryView.as_view(), name="group-chat-entry"),
]
