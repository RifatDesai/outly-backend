from django.db import transaction
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from .models import Group, GroupMembership, GroupPost, GroupJoinRequest
from .serializers import GroupSerializer, GroupMembershipSerializer, GroupPostSerializer, GroupJoinRequestSerializer

def ok(data, message="Success", code=200):
    return Response({"success": True, "message": message, "data": data, "errors": None, "meta": {}}, status=code)

def fail(message, code=400, errors=None):
    return Response({"success": False, "message": message, "data": None, "errors": errors or {}, "meta": {}}, status=code)

def active_membership(group, user):
    return group.memberships.filter(user=user, status=GroupMembership.Status.ACTIVE).first()

def can_manage(group, user):
    membership = active_membership(group, user)
    return bool(membership and membership.role in [GroupMembership.Role.OWNER, GroupMembership.Role.MODERATOR])

def ensure_group_chat(group, user):
    from chat.models import Conversation, ConversationParticipant
    conversation, _ = Conversation.objects.get_or_create(
        group=group, type=Conversation.Type.GROUP,
        defaults={"created_by": group.owner},
    )
    ConversationParticipant.objects.get_or_create(conversation=conversation, user=user)
    return conversation

class GroupListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=GroupSerializer(many=True))
    def get(self, request):
        groups = Group.objects.filter(is_active=True).filter(
            Q(visibility=Group.Visibility.PUBLIC)
            | Q(owner=request.user)
            | Q(memberships__user=request.user, memberships__status=GroupMembership.Status.ACTIVE)
        ).distinct()
        return ok(GroupSerializer(groups, many=True, context={"request": request}).data)

    @extend_schema(request=GroupSerializer, responses={201: GroupSerializer})
    def post(self, request):
        serializer = GroupSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return fail("Please correct the group details.", 400, serializer.errors)
        with transaction.atomic():
            group = serializer.save(owner=request.user)
            GroupMembership.objects.create(group=group, user=request.user, role=GroupMembership.Role.OWNER)
            ensure_group_chat(group, request.user)
        return ok(GroupSerializer(group, context={"request": request}).data, "Group created.", 201)

class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, group_id):
        return get_object_or_404(Group, pk=group_id, is_active=True)

    @extend_schema(responses=GroupSerializer)
    def get(self, request, group_id):
        group = self.get_object(request, group_id)
        if group.visibility == Group.Visibility.PRIVATE and not active_membership(group, request.user):
            return fail("This is a private group. Join the group to view its details.", 403)
        return ok(GroupSerializer(group, context={"request": request}).data)

    @extend_schema(request=GroupSerializer, responses=GroupSerializer)
    def patch(self, request, group_id):
        group = self.get_object(request, group_id)
        membership = active_membership(group, request.user)
        if not membership or membership.role != GroupMembership.Role.OWNER:
            return fail("Only the group owner can edit group details.", 403)
        serializer = GroupSerializer(group, data=request.data, partial=True, context={"request": request})
        if not serializer.is_valid():
            return fail("Please correct the group details.", 400, serializer.errors)
        serializer.save()
        return ok(serializer.data, "Group updated.")

    def delete(self, request, group_id):
        group = self.get_object(request, group_id)
        membership = active_membership(group, request.user)
        if not membership or membership.role != GroupMembership.Role.OWNER:
            return fail("Only the group owner can delete the group.", 403)
        from chat.models import Conversation
        Conversation.objects.filter(group=group).delete()
        group.is_active = False
        group.save(update_fields=["is_active", "updated_at"])
        return ok({}, "Group deleted.")

class GroupJoinLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        current = group.memberships.filter(user=request.user).first()
        if current and current.status == GroupMembership.Status.ACTIVE:
            return fail("You are already a member of this group.", 409)
        if group.visibility == Group.Visibility.PRIVATE:
            join_request, created = GroupJoinRequest.objects.get_or_create(group=group, user=request.user, defaults={"status": "PENDING"})
            if not created and join_request.status == "REJECTED":
                join_request.status = "PENDING"
                join_request.save(update_fields=["status", "updated_at"])
            if created or join_request.status == "PENDING":
                try:
                    from notifications.utils import create_notification
                    create_notification(group.owner, "GROUP_JOIN", "Group join request",
                                        f"{request.user.email} requested to join {group.name}.",
                                        actor=request.user, target_type="group", target_id=group.id)
                except Exception:
                    pass
                return ok(GroupJoinRequestSerializer(join_request).data, "Join request submitted.", 201)
            return fail("A join request has already been processed.", 409)
        membership, _ = GroupMembership.objects.update_or_create(
            group=group, user=request.user,
            defaults={"role": GroupMembership.Role.MEMBER, "status": GroupMembership.Status.ACTIVE},
        )
        ensure_group_chat(group, request.user)
        return ok(GroupMembershipSerializer(membership).data, "Joined group.", 201)

    def delete(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        membership = active_membership(group, request.user)
        if not membership:
            return fail("You are not a member of this group.", 404)
        if membership.role == GroupMembership.Role.OWNER:
            return fail("The owner cannot leave the group. Transfer ownership first.", 400)
        membership.status = GroupMembership.Status.REMOVED
        membership.save(update_fields=["status"])
        from chat.models import Conversation, ConversationParticipant
        conversation = Conversation.objects.filter(group=group, type="GROUP").first()
        if conversation:
            ConversationParticipant.objects.filter(conversation=conversation, user=request.user).delete()
        return ok({}, "Left group.")

class GroupMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        if group.visibility == "PRIVATE" and not active_membership(group, request.user):
            return fail("You must be a member to view this private group.", 403)
        members = group.memberships.filter(status="ACTIVE").select_related("user", "user__profile")
        return ok(GroupMembershipSerializer(members, many=True).data)

class GroupMemberActionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, group_id, user_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        actor = active_membership(group, request.user)
        target_user = get_object_or_404(User, pk=user_id)
        target = active_membership(group, target_user)
        if not actor or actor.role != "OWNER":
            return fail("Only the owner can change member roles.", 403)
        if not target:
            return fail("Active group member not found.", 404)
        if target.role == "OWNER":
            return fail("The owner's role cannot be changed here.", 400)
        role = request.data.get("role")
        if role not in ["MEMBER", "MODERATOR"]:
            return fail("role must be MEMBER or MODERATOR.", 400)
        target.role = role
        target.save(update_fields=["role"])
        return ok(GroupMembershipSerializer(target).data, "Member role updated.")

    def delete(self, request, group_id, user_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        actor = active_membership(group, request.user)
        target_user = get_object_or_404(User, pk=user_id)
        target = active_membership(group, target_user)
        if not actor or actor.role not in ["OWNER", "MODERATOR"]:
            return fail("Only the owner or a moderator can remove members.", 403)
        if not target:
            return fail("Active group member not found.", 404)
        if target.role == "OWNER" or (target.role == "MODERATOR" and actor.role != "OWNER") or target.user_id == request.user.id:
            return fail("You cannot remove this member.", 403)
        target.status = "REMOVED"
        target.save(update_fields=["status"])
        from chat.models import Conversation, ConversationParticipant
        conversation = Conversation.objects.filter(group=group, type="GROUP").first()
        if conversation:
            ConversationParticipant.objects.filter(conversation=conversation, user=target_user).delete()
        return ok({}, "Member removed.")

class GroupFeedView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=GroupPostSerializer(many=True))
    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        if group.visibility == "PRIVATE" and not active_membership(group, request.user):
            return fail("You must be a member to view this private group feed.", 403)
        posts = group.feed_posts.select_related("author", "author__profile")
        return ok(GroupPostSerializer(posts, many=True).data)

    @extend_schema(request=GroupPostSerializer, responses={201: GroupPostSerializer})
    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        if not active_membership(group, request.user):
            return fail("Only group members can post to the feed.", 403)
        serializer = GroupPostSerializer(data=request.data)
        if not serializer.is_valid():
            return fail("Please correct the post details.", 400, serializer.errors)
        post = serializer.save(group=group, author=request.user)
        try:
            from notifications.utils import create_notification
            for member in group.memberships.filter(status="ACTIVE").exclude(user=request.user).select_related("user"):
                create_notification(member.user, "GROUP_POST", f"New post in {group.name}",
                                    post.content[:500], actor=request.user,
                                    target_type="group", target_id=group.id)
        except Exception:
            pass
        return ok(GroupPostSerializer(post).data, "Group post created.", 201)

class GroupJoinRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        if not can_manage(group, request.user):
            return fail("Only the owner or a moderator can view join requests.", 403)
        items = group.join_requests.filter(status="PENDING").select_related("user", "user__profile")
        return ok(GroupJoinRequestSerializer(items, many=True).data)

    def post(self, request, group_id, request_id=None):
        if request_id is None:
            return fail("Provide a join request ID in the review URL.", 400)
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        if not can_manage(group, request.user):
            return fail("Only the owner or a moderator can review join requests.", 403)
        join_request = get_object_or_404(GroupJoinRequest, pk=request_id, group=group, status="PENDING")
        decision = request.data.get("decision")
        if decision not in ["ACCEPTED", "REJECTED"]:
            return fail("decision must be ACCEPTED or REJECTED.", 400)
        join_request.status = decision
        join_request.save(update_fields=["status", "updated_at"])
        if decision == "ACCEPTED":
            membership, _ = GroupMembership.objects.update_or_create(
                group=group, user=join_request.user,
                defaults={"role": "MEMBER", "status": "ACTIVE"},
            )
            ensure_group_chat(group, join_request.user)
        try:
            from notifications.utils import create_notification
            create_notification(join_request.user, "GROUP_JOIN", f"Group join request {decision.lower()}",
                                f"Your request to join {group.name} was {decision.lower()}.",
                                actor=request.user, target_type="group", target_id=group.id)
        except Exception:
            pass
        return ok(GroupJoinRequestSerializer(join_request).data, f"Join request {decision.lower()}.")

class GroupChatEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, is_active=True)
        if not active_membership(group, request.user):
            return fail("Only group members can open the group chat.", 403)
        conversation = ensure_group_chat(group, request.user)
        return ok({"conversation_id": conversation.id, "type": conversation.type, "group_id": group.id}, "Group chat ready.")
