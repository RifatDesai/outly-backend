from django.db import models


class Trail(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MODERATE = "MODERATE", "Moderate"
        HARD = "HARD", "Hard"

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    location = models.CharField(max_length=200)

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        blank=True,
    )

    distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    estimated_duration = models.CharField(
        max_length=100,
        blank=True,
    )

    facilities = models.JSONField(
        default=list,
        blank=True,
    )

    safety_notes = models.TextField(blank=True)

    images = models.JSONField(
        default=list,
        blank=True,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["difficulty"]),
        ]

    def __str__(self):
        return self.name


class TrailPoint(models.Model):
    trail = models.ForeignKey(
        Trail,
        on_delete=models.CASCADE,
        related_name="points",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
    )

    sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["trail", "sequence"],
                name="unique_trail_point_sequence",
            )
        ]

    def __str__(self):
        return f"{self.trail.name} - Point {self.sequence}"