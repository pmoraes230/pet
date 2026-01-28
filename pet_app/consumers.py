import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Mensagem, Tutor, Veterinario

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer responsável por gerenciar mensagens em tempo real
    entre Tutor e Veterinário.
    """

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.contact_id = int(self.scope["url_route"]["kwargs"]["contact_id"])

        # Sala única independente da ordem dos IDs
        ids = sorted([self.user.id, self.contact_id])
        self.room_group_name = f"chat_{ids[0]}_{ids[1]}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket conectado: {self.room_group_name}")

    async def disconnect(self, close_code):
        """
        Remove o socket do grupo apenas se a sala foi criada.
        Evita erro quando o connect falha antes da inicialização.
        """
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        conteudo = data.get("mensagem")

        if not conteudo:
            return

        mensagem = await self.save_message(conteudo)

        if not mensagem:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "mensagem": mensagem.CONTEUDO,
                "sender_id": self.user.id,
                "enviado_por": mensagem.ENVIADO_POR,
                "data_envio": mensagem.DATA_ENVIO.strftime("%H:%M"),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # ======================
    # Persistência no banco
    # ======================
    @database_sync_to_async
    def save_message(self, conteudo):
        tutor = None
        vet = None
        enviado_por = None

        # Usuário é Tutor
        try:
            tutor = Tutor.objects.get(user=self.user)
            vet = Veterinario.objects.get(id=self.contact_id)
            enviado_por = "TUTOR"
        except:
            pass

        # Usuário é Veterinário
        if not tutor:
            try:
                vet = Veterinario.objects.get(user=self.user)
                tutor = Tutor.objects.get(id=self.contact_id)
                enviado_por = "VETERINARIO"
            except:
                return None

        return Mensagem.objects.create(
            TUTOR=tutor,
            VETERINARIO=vet,
            CONTEUDO=conteudo,
            ENVIADO_POR=enviado_por,
            LIDA=False
        )
