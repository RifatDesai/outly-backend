from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import Notification
from .serializers import NotificationSerializer

def ok(data, message="Success", code=200):
    return Response({"success": True, "message": message, "data": data, "errors": None, "meta": {}}, status=code)

def fail(message, code=400):
    return Response({"success": False, "message": message, "data": None, "errors": {}, "meta": {}}, status=code)

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=NotificationSerializer(many=True))
    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user)
        unread = qs.filter(is_read=False).count()
        if request.query_params.get("unread_only", "").lower() in ["1", "true", "yes"]:
            qs = qs.filter(is_read=False)
        try:
            limit = min(max(int(request.query_params.get("limit", 50)), 1), 100)
        except ValueError:
            limit = 50
        items = NotificationSerializer(qs[:limit], many=True).data
        return ok({"notifications": items, "unread_count": unread, "limit": limit})

class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        item = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
        item.is_read = True
        item.save(update_fields=["is_read"])
        return ok(NotificationSerializer(item).data, "Notification marked as read.")

class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return ok({"updated_count": updated}, "All notifications marked as read.")
