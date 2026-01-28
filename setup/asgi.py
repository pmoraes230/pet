import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 🔹 Define settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

# 🔹 Inicializa o Django (CARREGA INSTALLED_APPS)
django_asgi_app = get_asgi_application()

import pet_app.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pet_app.routing.websocket_urlpatterns
        )
    ),
})
