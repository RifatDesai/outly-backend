from django.conf import settings
from django.db import models


class Activity(models.Model):

    class ActivityType(models.TextChoices):
        HIKE = "HIKE", "Hike"
        TRAIL_RUN = "TRAIL_RUN", "Trail Run"
        CYCLING = "CYCLING", "Cycling"
        CAMPING = "CAMPING", "Camping"
        MEETUP = "MEETUP", "Meetup"

    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MODERATE = "MODERATE", "Moderate"
        HARD = "HARD", "Hard"

    class Privacy(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        FOLLOWERS = "FOLLOWERS", "Followers"
        PRIVATE = "PRIVATE", "Private"

    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        COMPLETED = "COMPLETED", "Completed"

    title = models.CharField(max_length=150)

    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        default=ActivityType.HIKE
    )

    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_activities"
    )

    place_id = models.IntegerField(
        null=True,
        blank=True
    )

    trail_id = models.IntegerField(
        null=True,
        blank=True
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    start_at = models.DateTimeField(
        null=True,
        blank=True
    )

    end_at = models.DateTimeField(
        null=True,
        blank=True
    )

    distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    duration = models.CharField(
        max_length=100,
        blank=True
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        blank=True
    )

    notes = models.TextField(blank=True)

    privacy = models.CharField(
        max_length=20,
        choices=Privacy.choices,
        default=Privacy.PUBLIC
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["created_by", "created_at"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["start_at"]),
        ]

    def __str__(self):
        return self.title