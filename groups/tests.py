from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import GroupMembership
from chat.models import Conversation, ConversationParticipant

User = get_user_model()

class GroupAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", password="TestPass123!")
        self.member = User.objects.create_user(email="member@example.com", password="TestPass123!")

    def test_create_group_creates_owner_membership_and_group_chat(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post("/api/v1/groups/", {
            "name": "Bengaluru Trail Runners",
            "category": "Trail running",
            "description": "A weekend trail-running group.",
            "visibility": "PUBLIC",
            "rules": "Respect the trail.",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        group_id = response.data["data"]["id"]
        self.assertTrue(GroupMembership.objects.filter(group_id=group_id, user=self.owner, role="OWNER", status="ACTIVE").exists())
        self.assertTrue(Conversation.objects.filter(group_id=group_id, type="GROUP").exists())
        self.assertTrue(ConversationParticipant.objects.filter(conversation__group_id=group_id, user=self.owner).exists())

    def test_member_can_join_public_group_and_is_added_to_chat(self):
        group = __import__("groups.models", fromlist=["Group"]).Group.objects.create(
            name="Open group", category="Hiking", description="Open to everyone.", owner=self.owner
        )
        GroupMembership.objects.create(group=group, user=self.owner, role="OWNER")
        conversation = Conversation.objects.create(type="GROUP", group=group, created_by=self.owner)
        ConversationParticipant.objects.create(conversation=conversation, user=self.owner)
        self.client.force_authenticate(self.member)
        response = self.client.post(f"/api/v1/groups/{group.id}/join/", {}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ConversationParticipant.objects.filter(conversation=conversation, user=self.member).exists())
