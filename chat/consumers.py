from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from .models import Conversation, ConversationParticipant, Message

@database_sync_to_async
def is_conversation_member(conversation_id, user_id):
    return ConversationParticipant.objects.filter(conversation_id=conversation_id, user_id=user_id).exists()

@database_sync_to_async
def create_message(conversation_id, user, content):
    conversation = Conversation.objects.get(pk=conversation_id)
    message = Message.objects.create(conversation=conversation, sender=user, content=content)
    conversation.updated_at = timezone.now()
    conversation.save(update_fields=["updated_at"])
    profile = getattr(user, "profile", None)
    recipient_ids = list(conversation.participants.exclude(user=user).values_list("user_id", flat=True))
    return {
        "recipient_ids": recipient_ids,
        "id": message.id,
        "conversation": conversation.id,
        "sender_id": user.id,
        "sender_name": profile.display_name if profile and profile.display_name else user.email,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
        "edited_at": None,
        "is_deleted": False,
    }

@database_sync_to_async
def create_message_notifications(recipient_ids, actor, conversation_id):
    from notifications.utils import create_notification
    for recipient_id in recipient_ids:
        create_notification(
            recipient_id_to_user(recipient_id), "MESSAGE", "New message",
            f"New message from {actor.email}.", actor=actor,
            target_type="conversation", target_id=conversation_id,
        )

def recipient_id_to_user(user_id):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.get(pk=user_id)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return
        if not await is_conversation_member(self.conversation_id, user.id):
            await self.close(code=4403)
            return
        self.room_group_name = f"chat_{self.conversation_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        user = self.scope["user"]
        text = content.get("content") if isinstance(content, dict) else None
        if not isinstance(text, str) or not text.strip() or len(text.strip()) > 2000:
            await self.send_json({"type": "error", "message": "Message content must be 1-2000 characters."})
            return
        message = await create_message(self.conversation_id, user, text.strip())
        recipient_ids = message.pop("recipient_ids", [])
        if recipient_ids:
            try:
                await create_message_notifications(recipient_ids, user, self.conversation_id)
            except Exception:
                pass
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat.message", "message": message})

    async def chat_message(self, event):
        await self.send_json({"type": "message", "data": event["message"]})
