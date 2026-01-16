import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Mensagem, Veterinario, Tutor

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            self.contact_id = int(self.scope['url_route']['kwargs']['contact_id'])
            self.user = self.scope["user"]

            logger.info(
                f"WebSocket connect: user={self.user} | authenticated={self.user.is_authenticated}"
            )

            # 🔴 NÃO use user fake em produção
            if not self.user.is_authenticated:
                await self.close()
                return

            self.user_id = self.user.id

            # Nome único da sala (independente da ordem)
            user_ids = sorted([self.user_id, self.contact_id])
            self.room_name = f"{user_ids[0]}_{user_ids[1]}"
            self.room_group_name = f"chat_{self.room_name}"

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            logger.info(f"WebSocket conectado na sala {self.room_group_name}")

        except Exception as e:
            logger.error(f"Erro no connect: {e}", exc_info=True)
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            conteudo = data.get("mensagem")

            if not conteudo:
                return

            mensagem = await self.save_message(self.user, conteudo)

            if not mensagem:
                await self.send(text_data=json.dumps({
                    "error": "Erro ao salvar mensagem"
                }))
                return

            # 🔴 ENVIA O ID REAL DO REMETENTE
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

        except Exception as e:
            logger.error(f"Erro no receive: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                "error": "Erro ao processar mensagem"
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "mensagem": event["mensagem"],
            "sender_id": event["sender_id"],   # 🔴 ESSENCIAL
            "enviado_por": event["enviado_por"],
            "data_envio": event["data_envio"],
        }))

    # =========================
    # SALVAMENTO NO BANCO
    # =========================
    @database_sync_to_async
    def save_message(self, user, conteudo):
        tutor = None
        vet = None
        enviado_por = None

        # Usuário é TUTOR
        try:
            tutor = Tutor.objects.get(user=user)
            vet = Veterinario.objects.get(id=self.contact_id)
            enviado_por = "TUTOR"
        except (Tutor.DoesNotExist, Veterinario.DoesNotExist):
            pass

        # Usuário é VETERINARIO
        if not tutor:
            try:
                vet = Veterinario.objects.get(user=user)
                tutor = Tutor.objects.get(id=self.contact_id)
                enviado_por = "VETERINARIO"
            except (Veterinario.DoesNotExist, Tutor.DoesNotExist):
                return None

        if not tutor or not vet:
            return None

        return Mensagem.objects.create(
            TUTOR=tutor,
            VETERINARIO=vet,
            CONTEUDO=conteudo,
            ENVIADO_POR=enviado_por,
            LIDA=False
        )
