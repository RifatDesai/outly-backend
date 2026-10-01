from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from .models import Conversation, ConversationParticipant, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()

def ok(data, message="Success", code=200):
    return Response({"success": True, "message": message, "data": data, "errors": None, "meta": {}}, status=code)

def fail(message, code=400, errors=None):
    return Response({"success": False, "message": message, "data": None, "errors": errors or {}, "meta": {}}, status=code)

def get_member_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    if not conversation.participants.filter(user=request.user).exists():
        return None
    return conversation

class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ConversationSerializer(many=True))
    def get(self, request):
        ids = ConversationParticipant.objects.filter(user=request.user).values_list("conversation_id", flat=True)
        qs = Conversation.objects.filter(id__in=ids).select_related("group").prefetch_related("participants", "messages")
        return ok(ConversationSerializer(qs, many=True, context={"request": request}).data)

class DirectConversationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=inline_serializer(name="DirectConversationInput", fields={"user_id": serializers.IntegerField()}), responses={200: ConversationSerializer, 201: ConversationSerializer})
    def post(self, request):
        try:
            other_id = int(request.data.get("user_id"))
        except (TypeError, ValueError):
            return fail("user_id is required and must be an integer.", 400)
        if other_id == request.user.id:
            return fail("You cannot start a conversation with yourself.", 400)
        other = get_object_or_404(User, pk=other_id, is_active=True)
        try:
            from follows.models import Block
            if Block.objects.filter(blocker=request.user, blocked=other).exists() or Block.objects.filter(blocker=other, blocked=request.user).exists():
                return fail("A conversation cannot be started because one user has blocked the other.", 403)
        except ImportError:
            pass
        with transaction.atomic():
            candidates = Conversation.objects.filter(type=Conversation.Type.DIRECT, participants__user=request.user).filter(participants__user=other).annotate(participant_count=Count("participants", distinct=True)).filter(participant_count=2).distinct()
            conversation = candidates.first()
            created = conversation is None
            if created:
                conversation = Conversation.objects.create(type=Conversation.Type.DIRECT, created_by=request.user)
                ConversationParticipant.objects.bulk_create([
                    ConversationParticipant(conversation=conversation, user=request.user),
                    ConversationParticipant(conversation=conversation, user=other),
                ])
        return ok(ConversationSerializer(conversation, context={"request": request}).data,
                  "Conversation created." if created else "Conversation opened.", 201 if created else 200)

class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=MessageSerializer(many=True))
    def get(self, request, conversation_id):
        conversation = get_member_conversation(request, conversation_id)
        if conversation is None:
            return fail("You are not a participant in this conversation.", 403)
        participant = conversation.participants.get(user=request.user)
        participant.last_read_at = timezone.now()
        participant.save(update_fields=["last_read_at"])
        qs = conversation.messages.filter(is_deleted=False).select_related("sender", "sender__profile")
        return ok(MessageSerializer(qs, many=True, context={"request": request}).data)

    @extend_schema(request=inline_serializer(name="SendMessageInput", fields={"content": serializers.CharField(max_length=2000)}), responses={201: MessageSerializer})
    def post(self, request, conversation_id):
        conversation = get_member_conversation(request, conversation_id)
        if conversation is None:
            return fail("You are not a participant in this conversation.", 403)
        content = request.data.get("content")
        if not isinstance(content, str) or not content.strip():
            return fail("Message content is required.", 400, {"content": ["This field is required."]})
        if len(content.strip()) > 2000:
            return fail("Messages must be 2000 characters or fewer.", 400, {"content": ["Ensure this field has no more than 2000 characters."]})
        message = Message.objects.create(conversation=conversation, sender=request.user, content=content.strip())
        conversation.save(update_fields=["updated_at"])
        for participant in conversation.participants.exclude(user=request.user).select_related("user"):
            try:
                from notifications.utils import create_notification
                create_notification(participant.user, "MESSAGE", "New message", f"New message from {request.user.email}.", actor=request.user, target_type="conversation", target_id=conversation.id)
            except Exception:
                pass
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            layer = get_channel_layer()
            if layer:
                async_to_sync(layer.group_send)(f"chat_{conversation.id}", {
                    "type": "chat.message", "message": MessageSerializer(message).data
                })
        except Exception:
            pass
        return ok(MessageSerializer(message, context={"request": request}).data, "Message sent.", 201)

class ConversationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_member_conversation(request, conversation_id)
        if conversation is None:
            return fail("You are not a participant in this conversation.", 403)
        ConversationParticipant.objects.filter(conversation=conversation, user=request.user).update(last_read_at=timezone.now())
        return ok({}, "Conversation marked as read.")
