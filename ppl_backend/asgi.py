import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import scoring.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ppl_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            scoring.routing.websocket_urlpatterns
        )
    ),
})