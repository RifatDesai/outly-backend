from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from .models import PartnerRequest, PartnerRequestJoin

User = get_user_model()

class PartnerRequestAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", password="TestPass123!")
        self.explorer = User.objects.create_user(email="explorer@example.com", password="TestPass123!")

    def test_create_and_request_to_join(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post("/api/v1/partner-requests/", {
            "activity": "CYCLING",
            "destination": "Dehradun, Uttarakhand",
            "preferred_datetime": (timezone.now() + timedelta(days=10)).isoformat(),
            "spots_total": 2,
            "experience_level": "INTERMEDIATE",
            "description": "Looking for people to ride together.",
            "visibility": "PUBLIC",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        request_id = response.data["data"]["id"]
        self.client.force_authenticate(self.explorer)
        joined = self.client.post(f"/api/v1/partner-requests/{request_id}/join/", {"message": "I would like to join."}, format="json")
        self.assertEqual(joined.status_code, 201)
        self.assertTrue(PartnerRequestJoin.objects.filter(request_id=request_id, user=self.explorer, status="PENDING").exists())
