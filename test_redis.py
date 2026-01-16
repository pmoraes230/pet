#!/usr/bin/env python
"""
Script para testar conexão com Redis
"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠ python-dotenv not installed, skipping .env loading")

# Test 1: Verificar se REDIS_URL está definida
redis_url = os.getenv('REDIS_URL')
print(f"✓ REDIS_URL: {redis_url[:50]}..." if redis_url else "✗ REDIS_URL não definida")

# Test 2: Tentar conectar com redis-py
try:
    import redis
    r = redis.from_url(redis_url)
    ping = r.ping()
    print(f"✓ Redis connection successful: PING = {ping}")
except ImportError:
    print("✗ redis-py not installed. Install: pip install redis")
except Exception as e:
    print(f"✗ Redis connection failed: {e}")

# Test 3: Verificar channels_redis
try:
    from channels_redis.core import RedisChannelLayer
    print("✓ channels_redis importado com sucesso")
except ImportError:
    print("✗ channels_redis not installed. Install: pip install channels_redis")
except Exception as e:
    print(f"✗ channels_redis import error: {e}")

# Test 4: Verificar Django settings
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
    import django
    django.setup()
    
    from django.conf import settings
    
    if hasattr(settings, 'CHANNEL_LAYERS'):
        print("✓ CHANNEL_LAYERS configurada")
        print(f"  Backend: {settings.CHANNEL_LAYERS['default']['BACKEND']}")
        print(f"  Hosts: {settings.CHANNEL_LAYERS['default']['CONFIG']['hosts']}")
    else:
        print("✗ CHANNEL_LAYERS não configurada")
except Exception as e:
    print(f"✗ Django setup error: {e}")

print("\n" + "="*60)
print("Se todos os testes passaram, o WebSocket deve funcionar!")
print("="*60)
