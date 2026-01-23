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
            
            # 🔴 Busque o user via sessão (Tutor ou Veterinario)
            session = self.scope.get('session', {})
            user_id = session.get('user_id')
            user_role = session.get('user_role')  # 'tutor' ou 'vet'
            if not user_id or not user_role:
                logger.warning("Usuário não logado via sessão. Fechando WS.")
                await self.close()
                return
            
            self.user = await self.get_user(user_id, user_role)  # 🔴 Busca Tutor ou Vet
            if not self.user:
                logger.warning("Usuário não encontrado no banco. Fechando WS.")
                await self.close()
                return
            
            self.user_id = self.user.id  # ID do Tutor ou Vet
            self.user_role = user_role  # Armazene o role para uso posterior
            logger.info(f"WebSocket connect: user={self.user} | user_id={self.user_id} | role={self.user_role}")

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
        if self.user_role == 'tutor':
            try:
                tutor = user  # self.user já é o objeto Tutor
                vet = Veterinario.objects.get(id=self.contact_id)
                enviado_por = "TUTOR"
            except Veterinario.DoesNotExist:
                return None

        # Usuário é VETERINARIO
        elif self.user_role == 'vet':
            try:
                vet = user  # self.user já é o objeto Veterinario
                tutor = Tutor.objects.get(id=self.contact_id)
                enviado_por = "VETERINARIO"
            except Tutor.DoesNotExist:
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

    # =========================
    # 🔴 NOVO MÉTODO: Busca Tutor ou Veterinario pelo ID e role
    # =========================
    @database_sync_to_async
    def get_user(self, user_id, user_role):
        try:
            if user_role == 'tutor':
                return Tutor.objects.get(id=user_id)
            elif user_role == 'vet':
                return Veterinario.objects.get(id=user_id)
            else:
                return None
        except (Tutor.DoesNotExist, Veterinario.DoesNotExist):
            return None