# asgi.py
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack  # Adicione isso
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

import pet_app.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": SessionMiddlewareStack(  # Envolva com SessionMiddlewareStack
        AuthMiddlewareStack(  # Mantenha AuthMiddlewareStack se quiser, mas ele será ignorado para sessões
            URLRouter(pet_app.routing.websocket_urlpatterns)
        )
    ),
})