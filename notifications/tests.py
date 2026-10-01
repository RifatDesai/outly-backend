from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Notification

User = get_user_model()

class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="TestPass123!")
        self.other = User.objects.create_user(email="other@example.com", password="TestPass123!")
        self.notification = Notification.objects.create(recipient=self.user, actor=self.other, notification_type="FOLLOW", title="New follower")

    def test_user_can_list_and_mark_own_notification_read(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/notifications/")
        self.assertEqual(response.status_code, 200)
        read = self.client.post(f"/api/v1/notifications/{self.notification.id}/read/", {}, format="json")
        self.assertEqual(read.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
