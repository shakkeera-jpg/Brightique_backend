from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):

        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import UntypedToken
        from django.conf import settings
        from django.contrib.auth import get_user_model
        import jwt

        query_string = scope.get("query_string", b"").decode()
        token = parse_qs(query_string).get("token")

        if token:
            try:
                UntypedToken(token[0])

                decoded = jwt.decode(
                    token[0],
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                )

                user = await self.get_user(decoded["user_id"])
                scope["user"] = user

            except Exception as e:
                print("❌ JWT ERROR:", e)
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        print("🟢 WS USER:", scope["user"])  # 🔥 DEBUG LINE
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import AnonymousUser

        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
