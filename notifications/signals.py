from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from order.models import Order   


@receiver(post_save, sender=Order)
def order_created_notification(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user

    from notifications.models import Notification
    notification = Notification.objects.create(
        user=user,
        title="Order Placed 🎉",
        message=f"Your order #{instance.id} has been placed successfully!"
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "data": {   # ✅ THIS WAS MISSING
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
            }
        }
    )
