from .models import Notification

def create_notification(recipient, notification_type, title, body="", actor=None, target_type="", target_id=None):
    if recipient is None or (actor is not None and recipient.pk == actor.pk):
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        title=title,
        body=body,
        target_type=target_type,
        target_id=target_id,
    )
