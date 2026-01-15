from asgiref.sync import async_to_sync

def notify_user(user, title, message):
    # ⬇️ IMPORTS INSIDE FUNCTION (VERY IMPORTANT)
    from channels.layers import get_channel_layer
    from .models import Notification

    # Save notification in DB
    Notification.objects.create(
        user=user,
        title=title,
        message=message
    )

    # Send real-time notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "title": title,
            "message": message,
        }
    )
