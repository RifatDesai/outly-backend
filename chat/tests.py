from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Conversation, Message

User = get_user_model()

class ChatAPITests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email="sender@example.com", password="TestPass123!")
        self.receiver = User.objects.create_user(email="receiver@example.com", password="TestPass123!")

    def test_direct_conversation_and_message(self):
        self.client.force_authenticate(self.sender)
        response = self.client.post("/api/v1/chats/direct/", {"user_id": self.receiver.id}, format="json")
        self.assertEqual(response.status_code, 201)
        conversation_id = response.data["data"]["id"]
        sent = self.client.post(f"/api/v1/chats/conversations/{conversation_id}/messages/", {"content": "Hello!"}, format="json")
        self.assertEqual(sent.status_code, 201)
        self.assertTrue(Message.objects.filter(conversation_id=conversation_id, sender=self.sender, content="Hello!").exists())
        self.assertEqual(Conversation.objects.get(pk=conversation_id).participants.count(), 2)
