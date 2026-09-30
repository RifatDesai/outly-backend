
from django.conf import settings
from django.db import models


class Event(models.Model):
    class Category(models.TextChoices):
        HIKE = "HIKE", "Hike"
        TRAIL_RUN = "TRAIL_RUN", "Trail run"
        CYCLING = "CYCLING", "Cycling"
        CAMPING = "CAMPING", "Camping"
        MEETUP = "MEETUP", "Meetup"
        CLEANUP_DRIVE = "CLEANUP_DRIVE", "Cleanup drive"

    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MODERATE = "MODERATE", "Moderate"
        HARD = "HARD", "Hard"

    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        FOLLOWERS = "FOLLOWERS", "Followers only"
        INVITED = "INVITED", "Only invited"

    class ApprovalStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )

    # Optional links to existing places and trails.
    place = models.ForeignKey(
        "places.Place",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    trail = models.ForeignKey(
        "trails.Trail",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    location = models.CharField(max_length=255)
    meeting_point = models.CharField(max_length=255, blank=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField()

    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        blank=True,
    )

    requires_approval = models.BooleanField(default=False)

    visibility = models.CharField(
        max_length=15,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )

    # This is moderation of the event itself, not participant approval.
    approval_status = models.CharField(
        max_length=10,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_at"]
        indexes = [
            models.Index(fields=["start_at"]),
            models.Index(fields=["visibility", "approval_status"]),
            models.Index(fields=["organizer", "start_at"]),
        ]

    def __str__(self):
        return self.title


class EventParticipant(models.Model):
    class Status(models.TextChoices):
        INVITED = "INVITED", "Invited"
        PENDING = "PENDING", "Pending approval"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_participations",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.APPROVED,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"],
                name="unique_event_participant",
            )
        ]
        indexes = [
            models.Index(fields=["event", "status"]),
            models.Index(fields=["user", "status"]),
        ]
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.email} - {self.event.title}"
