import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "E_commerce.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from notifications.middleware import JWTAuthMiddleware
import notifications.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(notifications.routing.websocket_urlpatterns)
    ),
})
