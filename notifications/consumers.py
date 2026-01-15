from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs
import json

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user_from_token()
        if not self.user:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_user_from_token(self):
        query = parse_qs(self.scope["query_string"].decode())
        token_list = query.get("token")

        if not token_list:
            return None

        token = token_list[0]

        try:
            UntypedToken(token)
            payload = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return User.objects.get(id=payload.get("user_id"))
        except Exception:
            return None
