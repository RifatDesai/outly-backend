from django.urls import path
from .views import ConversationListView, DirectConversationView, ConversationMessagesView, ConversationReadView

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="conversation-list"),
    path("direct/", DirectConversationView.as_view(), name="direct-conversation"),
    path("conversations/<int:conversation_id>/messages/", ConversationMessagesView.as_view(), name="conversation-messages"),
    path("conversations/<int:conversation_id>/read/", ConversationReadView.as_view(), name="conversation-read"),
]
