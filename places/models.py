from django.db import models


class Place(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MODERATE = "MODERATE", "Moderate"
        HARD = "HARD", "Hard"

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    coordinates = models.JSONField()

    category = models.CharField(max_length=100)

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

    def __str__(self):
        return self.name
