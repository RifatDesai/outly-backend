from rest_framework import serializers
from .models import Conversation, ConversationParticipant, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    sender_name = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender_id", "sender_name", "content", "created_at", "edited_at", "is_deleted", "is_mine"]
        read_only_fields = ["id", "conversation", "sender_id", "sender_name", "created_at", "edited_at", "is_deleted", "is_mine"]

    def get_sender_name(self, obj):
        profile = getattr(obj.sender, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.sender.email

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.sender_id == request.user.id)

class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    group_id = serializers.IntegerField(read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True, default=None)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "type", "group_id", "group_name", "participants", "last_message", "unread_count", "created_at", "updated_at"]

    def get_participants(self, obj):
        request = self.context.get("request")
        qs = obj.participants.select_related("user", "user__profile")
        result = []
        for p in qs:
            profile = getattr(p.user, "profile", None)
            result.append({
                "id": p.user_id,
                "display_name": profile.display_name if profile and profile.display_name else p.user.email,
                "username": profile.username if profile else "",
            })
        return result

    def get_last_message(self, obj):
        message = obj.messages.filter(is_deleted=False).select_related("sender").order_by("-created_at").first()
        if not message:
            return None
        profile = getattr(message.sender, "profile", None)
        return {"id": message.id, "sender_id": message.sender_id,
                "sender_name": profile.display_name if profile and profile.display_name else message.sender.email,
                "content": message.content, "created_at": message.created_at}

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        participant = obj.participants.filter(user=request.user).first()
        if not participant:
            return 0
        qs = obj.messages.filter(is_deleted=False).exclude(sender=request.user)
        if participant.last_read_at:
            qs = qs.filter(created_at__gt=participant.last_read_at)
        return qs.count()
