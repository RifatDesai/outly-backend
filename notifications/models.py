from django.conf import settings
from django.db import models

class Notification(models.Model):
    class Type(models.TextChoices):
        FOLLOW = "FOLLOW", "Follow"
        LIKE = "LIKE", "Like"
        COMMENT = "COMMENT", "Comment"
        MESSAGE = "MESSAGE", "Message"
        GROUP_JOIN = "GROUP_JOIN", "Group join"
        GROUP_POST = "GROUP_POST", "Group post"
        PARTNER_REQUEST = "PARTNER_REQUEST", "Partner request"
        PARTNER_JOIN = "PARTNER_JOIN", "Partner join request"
        SYSTEM = "SYSTEM", "System"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="outly_notifications")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="outly_notifications_sent")
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=180)
    body = models.CharField(max_length=500, blank=True)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.PositiveBigIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification {self.pk} for {self.recipient_id}"
