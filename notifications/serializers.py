from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    actor_id = serializers.IntegerField(source="actor.id", read_only=True, allow_null=True)
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["id", "actor_id", "actor_name", "notification_type", "title", "body",
                  "target_type", "target_id", "is_read", "created_at"]
        read_only_fields = fields

    def get_actor_name(self, obj):
        if not obj.actor:
            return None
        profile = getattr(obj.actor, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.actor.email
