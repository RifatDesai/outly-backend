from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    username = models.CharField(
        max_length=50,
        unique=True,
    )

    display_name = models.CharField(
        max_length=100,
        blank=True,
    )

    photo = models.URLField(
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    interests = models.JSONField(
        default=list,
        blank=True,
    )

    privacy_settings = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.username