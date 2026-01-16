#!/usr/bin/env python
"""
Script de diagnóstico para WebSocket
Verifica se toda a configuração está carregando corretamente
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

print("="*70)
print("🔍 DIAGNÓSTICO DO WEBSOCKET")
print("="*70)

# Test 1: Django Setup
print("\n[1] Inicializando Django...")
try:
    import django
    django.setup()
    print("✓ Django carregado com sucesso")
except Exception as e:
    print(f"✗ Erro ao carregar Django: {e}")
    sys.exit(1)

# Test 2: Verificar settings
print("\n[2] Verificando settings.py...")
try:
    from django.conf import settings
    
    # Verificar CHANNEL_LAYERS
    if hasattr(settings, 'CHANNEL_LAYERS'):
        print("✓ CHANNEL_LAYERS configurada")
        hosts = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts']
        print(f"  └─ Hosts: {hosts[0][:50]}...")
    else:
        print("✗ CHANNEL_LAYERS não está em settings.py")
        
    # Verificar ASGI_APPLICATION
    if hasattr(settings, 'ASGI_APPLICATION'):
        print(f"✓ ASGI_APPLICATION: {settings.ASGI_APPLICATION}")
    else:
        print("✗ ASGI_APPLICATION não está em settings.py")
        
    # Verificar channels em INSTALLED_APPS
    if 'channels' in settings.INSTALLED_APPS:
        print("✓ 'channels' está em INSTALLED_APPS")
    else:
        print("✗ 'channels' NÃO está em INSTALLED_APPS")
        
except Exception as e:
    print(f"✗ Erro ao verificar settings: {e}")
    sys.exit(1)

# Test 3: Carregar asgi.py
print("\n[3] Carregando setup/asgi.py...")
try:
    from setup import asgi
    print("✓ setup/asgi.py importado com sucesso")
    
    if hasattr(asgi, 'application'):
        print(f"✓ application está definida: {asgi.application}")
    else:
        print("✗ application NÃO está definida em asgi.py")
        
except Exception as e:
    print(f"✗ Erro ao importar asgi.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Carregar routing
print("\n[4] Carregando pet_app/routing.py...")
try:
    from pet_app import routing
    print("✓ pet_app/routing.py importado com sucesso")
    
    if hasattr(routing, 'websocket_urlpatterns'):
        patterns = routing.websocket_urlpatterns
        print(f"✓ websocket_urlpatterns definida com {len(patterns)} padrão(s)")
        for i, pattern in enumerate(patterns):
            print(f"  └─ Padrão {i+1}: {pattern.pattern}")
    else:
        print("✗ websocket_urlpatterns NÃO está definida")
        
except Exception as e:
    print(f"✗ Erro ao importar routing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Carregar consumer
print("\n[5] Carregando pet_app/consumers.py...")
try:
    from pet_app import consumers
    print("✓ pet_app/consumers.py importado com sucesso")
    
    if hasattr(consumers, 'ChatConsumer'):
        print("✓ ChatConsumer classe encontrada")
        # Verificar se tem os métodos necessários
        methods = ['connect', 'disconnect', 'receive', 'chat_message', 'save_message']
        for method in methods:
            if hasattr(consumers.ChatConsumer, method):
                print(f"  ✓ Método '{method}' existe")
            else:
                print(f"  ✗ Método '{method}' NÃO existe")
    else:
        print("✗ ChatConsumer NÃO foi encontrada")
        
except Exception as e:
    print(f"✗ Erro ao importar consumers: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Verificar Redis
print("\n[6] Testando conexão com Redis...")
try:
    import redis
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    r = redis.from_url(redis_url)
    if r.ping():
        print(f"✓ Redis conectado: {redis_url[:50]}...")
    else:
        print("✗ Redis PING falhou")
except ImportError:
    print("✗ redis-py não instalado")
except Exception as e:
    print(f"✗ Erro na conexão Redis: {e}")

# Test 7: Verificar Models
print("\n[7] Verificando models...")
try:
    from pet_app.models import Mensagem, Tutor, Veterinario
    print("✓ Models importadas com sucesso")
    print(f"  ✓ Mensagem: {Mensagem}")
    print(f"  ✓ Tutor: {Tutor}")
    print(f"  ✓ Veterinario: {Veterinario}")
except Exception as e:
    print(f"✗ Erro ao importar models: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✨ Se todos os testes passaram, o WebSocket deve funcionar!")
print("="*70)
print("\n📝 Próximos passos:")
print("1. Reinicie o Daphne")
print("2. Acesse http://localhost:8000/mensagens/")
print("3. Verifique F12 → Console")
print("4. Procure por 'WebSocket' nos logs")
