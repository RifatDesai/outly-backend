from django.conf import settings
from django.db import models

class PartnerRequest(models.Model):
    class Activity(models.TextChoices):
        HIKE = "HIKE", "Hike"
        TRAIL_RUN = "TRAIL_RUN", "Trail run"
        CYCLING = "CYCLING", "Cycling"
        CAMPING = "CAMPING", "Camping"
        MEETUP = "MEETUP", "Meetup"
    class Experience(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        PRIVATE = "PRIVATE", "Private"
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="partner_requests")
    activity = models.CharField(max_length=20, choices=Activity.choices)
    destination = models.CharField(max_length=200)
    preferred_datetime = models.DateTimeField()
    spots_total = models.PositiveSmallIntegerField(default=1)
    experience_level = models.CharField(max_length=15, choices=Experience.choices, default=Experience.BEGINNER)
    description = models.TextField(max_length=1500)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["preferred_datetime", "-created_at"]

    @property
    def spots_filled(self):
        return self.join_requests.filter(status="ACCEPTED").count()

    def __str__(self):
        return f"{self.get_activity_display()} - {self.destination}"

class PartnerRequestJoin(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    request = models.ForeignKey(PartnerRequest, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="partner_request_joins")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    message = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["request", "user"], name="unique_partner_request_join")]
        ordering = ["-created_at"]
