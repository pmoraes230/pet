# WebSocket Real-Time Chat - Setup Guide

## ✅ Mudanças Implementadas

### 1. **Consumer atualizado** ([pet_app/consumers.py](pet_app/consumers.py))
   - Agora aceita apenas 1 ID (`contact_id`) pela URL
   - Obtém o ID do usuário logado da sessão
   - Suporta tanto tutor → vet quanto vet → tutor

### 2. **Routing corrigido** ([pet_app/routing.py](pet_app/routing.py))
   - URL WebSocket: `ws/chat/<contact_id>/`
   - Exemplo: `ws://localhost:8000/ws/chat/5/`

### 3. **Settings.py atualizado** ([setup/settings.py](setup/settings.py))
   - CHANNEL_LAYERS usando REDIS_URL correto
   - Default: `redis://localhost:6379/0`
   - Em produção, defina `REDIS_URL` na variável de ambiente

### 4. **Templates atualizadas**
   - [tutor_dash/templates/mensagens.html](tutor_dash/templates/mensagens.html)
   - [vet_dash/templates/mensagensvet.html](vet_dash/templates/mensagensvet.html)
   - Ambas com erro handler para melhor debug

## 🚀 Como rodar localmente

### Pré-requisitos
```bash
pip install channels channels_redis
```

### 1. Inicie o Redis (necessário para WebSocket)
```bash
# Windows (se tiver WSL2 ou Docker)
docker run -p 6379:6379 redis:latest

# Ou instale Redis localmente no Windows
# Download: https://github.com/microsoftarchive/redis/releases
```

### 2. Verifique se Redis está rodando
```bash
redis-cli ping
# Deve retornar: PONG
```

### 3. Configure o .env
```
REDIS_URL=redis://localhost:6379/0
```

### 4. Rode o servidor Django com Daphne (suporta WebSocket)
```bash
pip install daphne
daphne -b 0.0.0.0 -p 8000 setup.asgi:application
```

## 🧪 Teste o WebSocket

### Opção 1: Browser Console
1. Abra a página de mensagens (tutor ou vet)
2. Selecione um contato
3. Abra DevTools (F12) → Console
4. Verifique se há erro no WebSocket:
```javascript
// Deve estar conectado
console.log(socket); // WebSocket { ... }
console.log(socket.readyState); // 1 = OPEN
```

### Opção 2: Teste via CLI
```bash
pip install websocket-client

# Teste de conexão
python -c "
from websocket import WebSocketApp
import json

def on_message(ws, msg):
    print('Recebido:', msg)

ws = WebSocketApp('ws://localhost:8000/ws/chat/1/')
ws.on_message = on_message
ws.run_forever()
"
```

## 📝 Fluxo de Mensagem em Tempo Real

1. **Tutor/Vet envia mensagem** via form
2. **WebSocket intercepta** e envia JSON via `socket.send()`
3. **Consumer recebe** em `receive()` method
4. **Salva no banco** via `save_message()` (async)
5. **Envia para grupo** via `group_send()`
6. **Todos no room recebem** via `chat_message()` event
7. **JavaScript renderiza** a mensagem no chat em tempo real

## 🐛 Troubleshooting

### "WebSocket connection closed"
```
❌ Redis não está rodando
✅ Solução: Verifique se Redis está ativo (redis-cli ping)
```

### "Erro 500 no WebSocket"
```
❌ Consumer.py tem erro
✅ Solução: Verifique logs do Daphne
```

### Mensagens não aparecem em tempo real
```
❌ Socket não está conectado (readyState != 1)
✅ Solução: Verifique console do browser (F12)
```

### "404 - WebSocket route not found"
```
❌ Routing.py ou asgi.py incorretos
✅ Solução: Verifique se pet_app.routing está importado em setup/asgi.py
```

## 📦 Estrutura de Arquivos

```
pet_app/
├── consumers.py          # Consumer WebSocket
├── routing.py            # URL patterns WebSocket
├── models.py             # Modelo Mensagem

setup/
├── asgi.py               # ASGI config com WebSocket
├── settings.py           # CHANNEL_LAYERS config

tutor_dash/templates/
├── mensagens.html        # Chat Tutor

vet_dash/templates/
├── mensagensvet.html     # Chat Veterinário
```

## ✨ Próximos Passos (Opcional)

- [ ] Adicionar notificações (quando nova mensagem chega)
- [ ] Indicador de "digitando"
- [ ] Salvar histórico com paginação
- [ ] Enviar arquivos/imagens
- [ ] Usar protocol frames para melhor performance

