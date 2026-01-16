# 🚀 Tutorial Completo: Implementar WebSocket em Tempo Real com Django Channels

## 📌 Objetivo
Implementar um sistema de **mensagens em tempo real** entre Tutores e Veterinários usando **WebSocket** com Django Channels.

---

## 📦 Pré-requisitos

### Pacotes Necessários
```bash
pip install channels channels_redis daphne redis python-decouple
```

Verificar instalação:
```bash
pip list | grep -E "channels|daphne|redis"
```

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR (Cliente)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Template HTML (mensagens.html)                  │   │
│  │  - JavaScript WebSocket                          │   │
│  │  - ws://127.0.0.1:8000/ws/chat/<contact_id>/   │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────┘
                 │ WebSocket
                 ↓
┌─────────────────────────────────────────────────────────┐
│                   DAPHNE (ASGI Server)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  setup/asgi.py                                   │   │
│  │  - ProtocolTypeRouter (HTTP + WebSocket)         │   │
│  │  - URLRouter → pet_app.routing                   │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────┐
│              CHANNELS (WebSocket Handler)                │
│  ┌──────────────────────────────────────────────────┐   │
│  │  pet_app/consumers.py (ChatConsumer)             │   │
│  │  - connect() → Autoriza usuário                  │   │
│  │  - receive() → Recebe mensagem do cliente        │   │
│  │  - group_send() → Envia para todos no chat room  │   │
│  │  - save_message() → Salva no banco de dados      │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────┘
                 │
         ┌───────┴────────┐
         ↓                ↓
    ┌─────────┐    ┌─────────────┐
    │ Django  │    │ Redis Layer │
    │  ORM    │    │  (Message   │
    │         │    │  Broker)    │
    └─────────┘    └─────────────┘
```

---

## 🔧 Passo 1: Instalar e Configurar Channels

### 1.1. settings.py
Adicione ao `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... apps padrão ...
    'channels',
]
```

### 1.2. Configurar ASGI
Altere a variável padrão do Django:

```python
# Em settings.py
ASGI_APPLICATION = 'setup.asgi.application'
```

---

## 🗳️ Passo 2: Criar Consumer (WebSocket Handler)

### 2.1. Arquivo: `pet_app/consumers.py`

```python
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Mensagem, Veterinario, Tutor
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer para chat em tempo real.
    
    Fluxo:
    1. Cliente conecta via WebSocket
    2. Consumer autoriza o usuário
    3. Adiciona consumer ao "group" (sala de chat)
    4. Consumer recebe mensagens do cliente
    5. Salva no banco e envia para todos no grupo
    """
    
    async def connect(self):
        """Chamado quando cliente conecta via WebSocket"""
        try:
            # Pega o ID do contato pela URL
            self.contact_id = int(self.scope['url_route']['kwargs']['contact_id'])
            user = self.scope["user"]
            
            logger.info(f"WebSocket connect: user={user}, authenticated={user.is_authenticated}")
            
            # Verifica se usuário está logado
            if not user.is_authenticated:
                logger.warning("User not authenticated, closing connection")
                await self.close()
                return
            
            # Pega ID do usuário logado
            self.user_id = user.id
            
            # Cria uma "sala de chat" única entre dois usuários
            # Usa sorted para garantir consistência (1_5 == 5_1)
            user_ids = sorted([self.user_id, self.contact_id])
            self.room_name = f"{user_ids[0]}_{user_ids[1]}"
            self.room_group_name = f'chat_{self.room_name}'

            # Adiciona este consumer ao grupo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Aceita a conexão
            await self.accept()
            logger.info(f"WebSocket accepted for room: {self.room_group_name}")
            
        except Exception as e:
            logger.error(f"WebSocket connect error: {e}", exc_info=True)
            await self.close()

    async def disconnect(self, close_code):
        """Chamado quando cliente desconecta"""
        if hasattr(self, 'room_group_name'):
            # Remove este consumer do grupo
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Chamado quando cliente envia uma mensagem"""
        try:
            # Parse do JSON enviado pelo cliente
            text_data_json = json.loads(text_data)
            conteudo = text_data_json['mensagem']

            user = self.scope["user"]
            if not user.is_authenticated:
                await self.send(text_data=json.dumps({'error': 'Não autenticado'}))
                return

            # Salva mensagem no banco de dados
            mensagem = await self.save_message(user, conteudo)
            if not mensagem:
                await self.send(text_data=json.dumps({'error': 'Erro ao salvar mensagem'}))
                return

            # Envia a mensagem para TODOS no grupo (broadcast)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',  # Chama método chat_message() em todos
                    'mensagem': mensagem.CONTEUDO,
                    'enviado_por': mensagem.ENVIADO_POR,
                    'data_envio': mensagem.DATA_ENVIO.strftime("%H:%M"),
                }
            )
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}", exc_info=True)
            await self.send(text_data=json.dumps({'error': f'Erro: {str(e)}'}))

    async def chat_message(self, event):
        """
        Chamado quando group_send() é executado.
        Envia a mensagem do evento para o cliente.
        """
        await self.send(text_data=json.dumps({
            'mensagem': event['mensagem'],
            'enviado_por': event['enviado_por'],
            'data_envio': event['data_envio'],
        }))

    @database_sync_to_async
    def save_message(self, user, conteudo):
        """
        Salva mensagem no banco de dados.
        
        Descobre se o usuário logado é Tutor ou Veterinário
        e relaciona com o contato correspondente.
        """
        tutor = None
        vet = None
        enviado_por = None

        try:
            # Tenta como Tutor
            tutor_profile = Tutor.objects.get(user=user)
            tutor = tutor_profile
            vet = Veterinario.objects.get(id=self.contact_id)
            enviado_por = 'TUTOR'
        except (Tutor.DoesNotExist, Veterinario.DoesNotExist):
            pass

        if not tutor:
            try:
                # Tenta como Veterinário
                vet_profile = Veterinario.objects.get(user=user)
                vet = vet_profile
                tutor = Tutor.objects.get(id=self.contact_id)
                enviado_por = 'VETERINARIO'
            except (Veterinario.DoesNotExist, Tutor.DoesNotExist):
                return None

        if not tutor or not vet:
            return None

        # Cria a mensagem no banco
        return Mensagem.objects.create(
            TUTOR=tutor,
            VETERINARIO=vet,
            CONTEUDO=conteudo,
            ENVIADO_POR=enviado_por,
            LIDA=False
        )
```

---

## 🌐 Passo 3: Configurar Routing (URLs do WebSocket)

### 3.1. Arquivo: `pet_app/routing.py`

```python
from django.urls import re_path
from . import consumers

# URL patterns para WebSocket
websocket_urlpatterns = [
    # Padrão: ws/chat/<contact_id>/
    # Exemplo: ws/chat/5/
    re_path(r'^ws/chat/(?P<contact_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
```

**Explicação do regex:**
- `^` = início da string
- `ws/chat/` = caminho literal
- `(?P<contact_id>\d+)` = grupo nomeado "contact_id" que captura dígitos
- `/$` = barra e fim da string

---

## ⚙️ Passo 4: Configurar ASGI (setup/asgi.py)

```python
import os
import django

# IMPORTANTE: django.setup() ANTES de imports de apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import pet_app.routing 

# ProtocolTypeRouter: roteia por protocolo (HTTP ou WebSocket)
application = ProtocolTypeRouter({
    # HTTP segue o fluxo Django normal
    "http": get_asgi_application(),
    
    # WebSocket passa por:
    # 1. AuthMiddlewareStack = autenticação (user logado)
    # 2. URLRouter = routing por URL
    # 3. pet_app.routing.websocket_urlpatterns = URL patterns
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pet_app.routing.websocket_urlpatterns
        )
    ),
})
```

---

## 📨 Passo 5: Configurar Redis (Message Broker)

### 5.1. Arquivo: `.env`

```env
# URL do Redis (local ou cloud)
# Local: redis://localhost:6379/0
# Cloud: redis://user:password@host:port/db
REDIS_URL=redis://default:sua_senha@redis-xxxxx.redislabs.com:15853
```

### 5.2. Arquivo: `setup/settings.py`

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            # Lista com URL(s) do Redis
            "hosts": [os.getenv("REDIS_URL", "redis://localhost:6379/0")],
            # Desabilita SSL se tiver problemas (usar redis:// ao invés de rediss://)
            "ssl_cert_reqs": None,
        },
    },
}
```

---

## 🌍 Passo 6: Templates (Frontend)

### 6.1. Script JavaScript em `mensagens.html` ou `mensagensvet.html`

```javascript
<script>
    // ID do contato (tutor ou veterinário)
    const contactId = "{{ contato_selecionado.id }}";
    
    if (contactId) {
        // Conecta ao WebSocket
        const socket = new WebSocket(
            'ws://' + window.location.host + '/ws/chat/' + contactId + '/'
        );

        // Quando mensagem chega do servidor
        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            
            // Renderiza mensagem no chat
            const msgDiv = document.createElement('div');
            // ... adiciona classe conforme enviado_por ...
            // ... adiciona ao chat-box ...
            
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        };

        // Quando houver erro
        socket.onerror = function(e) {
            console.error('Erro no WebSocket:', e);
        };

        // Quando a conexão fechar
        socket.onclose = function(e) {
            console.error('Chat socket fechou inesperadamente');
        };

        // Intercepta submissão do form
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = form.querySelector('input[name="mensagem"]');
            const mensagem = input.value.trim();

            if (mensagem && socket.readyState === WebSocket.OPEN) {
                // Envia JSON para o servidor
                socket.send(JSON.stringify({
                    'mensagem': mensagem
                }));
                input.value = '';
            }
        });
    }
</script>
```

---

## 🚀 Passo 7: Rodar o Servidor

### ⚠️ **IMPORTANTE**: NÃO usar `python manage.py runserver`

O servidor padrão do Django **não suporta WebSocket**. Use **Daphne**:

```bash
# Opção 1: Direto
python -m daphne -b 0.0.0.0 -p 8000 setup.asgi:application

# Opção 2: Com venv (Windows)
C:/Users/seu_usuario/Documents/pet/venv/Scripts/python.exe -m daphne -b 0.0.0.0 -p 8000 setup.asgi:application

# Opção 3: Task do VS Code (Ctrl+Shift+B)
# Configure em .vscode/tasks.json
```

---

## 🧪 Passo 8: Testar

### 8.1. Verificar Redis
```bash
python -c "
import redis
r = redis.from_url('redis://localhost:6379/0')
print('Redis OK!' if r.ping() else 'Redis falhou')
"
```

### 8.2. Testar no Navegador
1. Abra `http://localhost:8000/mensagens/`
2. Selecione um veterinário
3. Abra DevTools (F12) → Console
4. Digite: `socket.readyState` (deve ser `1` = OPEN)
5. Envie uma mensagem
6. Deve aparecer em tempo real em ambas as abas

### 8.3. Script de Diagnóstico
```bash
python test_redis.py
```

Verifica:
- ✓ REDIS_URL está definida
- ✓ Conecta ao Redis
- ✓ channels_redis instalado
- ✓ CHANNEL_LAYERS configurado

---

## 🐛 Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `404 /ws/chat/3/` | Routing incorreto | Verifique `pet_app/routing.py` e `asgi.py` |
| `WebSocket connection failed` | Redis desconectado | `python test_redis.py` |
| `readyState: 3 (CLOSED)` | Consumer rejeitou conexão | Verifique logs do Daphne, usuário autenticado? |
| `[SSL: WRONG_VERSION_NUMBER]` | URL Redis com `rediss://` em porta errada | Use `redis://` ao invés de `rediss://` |
| `Apps aren't loaded yet` | django.setup() no lugar errado | Mova para inicio do `asgi.py` |

---

## 📊 Fluxo Completo de Mensagem

```
1. Usuário digita mensagem no navegador
   ↓
2. JavaScript: socket.send(JSON.stringify({mensagem: 'Oi'}))
   ↓
3. WebSocket transmite ao servidor Daphne
   ↓
4. ChatConsumer.receive() processa
   ↓
5. save_message() salva no banco de dados
   ↓
6. group_send() envia para todos no grupo (broadcast)
   ↓
7. chat_message() event handler em cada consumer
   ↓
8. socket.send() envia JSON para cada cliente conectado
   ↓
9. JavaScript socket.onmessage() renderiza no DOM
   ↓
10. Mensagem aparece em tempo real ✨
```

---

## 📚 Recursos Úteis

- [Django Channels Docs](https://channels.readthedocs.io/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [WebSocket MDN Docs](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Async/Await Python](https://docs.python.org/3/library/asyncio.html)

---

## ✅ Checklist Final

- [ ] Instalou `channels`, `channels_redis`, `daphne`
- [ ] Criou `pet_app/consumers.py` com ChatConsumer
- [ ] Criou `pet_app/routing.py` com websocket_urlpatterns
- [ ] Atualizou `setup/asgi.py` com ProtocolTypeRouter
- [ ] Configurou `CHANNEL_LAYERS` em `settings.py`
- [ ] Adicionou `REDIS_URL` no `.env`
- [ ] Rodar com Daphne (não runserver)
- [ ] Testou no navegador (F12 → Console)
- [ ] Verificou `socket.readyState === 1` (OPEN)

---

**Se seguiu todos os passos corretamente, seu chat deve estar funcionando em tempo real! 🎉**

