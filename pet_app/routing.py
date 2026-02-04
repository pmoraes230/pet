from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<contact_id>[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}|[0-9a-f]{32})/?$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/notificacoes/(?P<role>tutor|vet)/(?P<user_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$', consumers.NotificacaoConsumer.as_asgi()),
]