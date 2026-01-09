#!/usr/bin/env python
"""
Script para testar configuração de email do Django com diagnóstico detalhado
"""
import os
import sys
import django
import socket
import smtplib

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("TESTE DE CONFIGURAÇÃO DE EMAIL - DIAGNÓSTICO")
print("=" * 60)

# Mostrar configurações
print("\n📧 Configurações detectadas:")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Validar que as variáveis estão preenchidas
if not settings.EMAIL_HOST_USER:
    print("\n❌ ERRO: EMAIL_HOST_USER não está definido no .env")
    sys.exit(1)

if not settings.EMAIL_HOST_PASSWORD:
    print("\n❌ ERRO: EMAIL_HOST_PASSWORD não está definido no .env")
    sys.exit(1)

print("\n✅ Configurações parecem válidas!")

# Teste 1: Conectividade
print("\n" + "=" * 60)
print("TESTE 1: Conectividade com servidor SMTP")
print("=" * 60)

try:
    print(f"🔄 Tentando conectar a {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
    socket.create_connection((settings.EMAIL_HOST, settings.EMAIL_PORT), timeout=5)
    print(f"✅ Conexão bem-sucedida!")
except socket.timeout:
    print(f"❌ TIMEOUT: Não conseguiu conectar em 5 segundos")
    print("   Possível causa: Firewall bloqueando porta 587 ou problema de rede")
    sys.exit(1)
except socket.gaierror as e:
    print(f"❌ ERRO de DNS: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERRO de conexão: {e}")
    sys.exit(1)

# Teste 2: Tentar autenticação SMTP
print("\n" + "=" * 60)
print("TESTE 2: Autenticação SMTP")
print("=" * 60)

try:
    print(f"🔄 Tentando fazer login no SMTP...")
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print(f"✅ Login bem-sucedido!")
    server.quit()
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ ERRO de autenticação: {e}")
    print("   Verifique se a senha de app está correta no .env")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERRO: {e}")
    sys.exit(1)

# Teste 3: Enviar email via Django
print("\n" + "=" * 60)
print("TESTE 3: Enviar email via Django")
print("=" * 60)

try:
    print(f"🔄 Tentando enviar email de teste (com timeout de 15s)...")
    resultado = send_mail(
        subject='Teste de Email - Coração em Patas',
        message='Se você recebeu este email, a configuração está funcionando! 🎉',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    print(f"✅ Email enviado com sucesso! (send_mail retornou: {resultado})")
    print(f"\n📨 Verifique a caixa de entrada de: {settings.EMAIL_HOST_USER}")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ ERRO de autenticação ao enviar:")
    print(f"   {e}")
    print("\n   Dicas:")
    print("   1. Verifique se 2FA está ativado no Gmail")
    print("   2. Gere uma nova Senha de App em: https://myaccount.google.com/apppasswords")
    print("   3. Copie a senha SEM ESPAÇOS no .env")
    
except smtplib.SMTPException as e:
    print(f"❌ ERRO SMTP: {e}")
    
except Exception as e:
    print(f"❌ ERRO ao enviar email:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    print("\nStack trace completo:")
    traceback.print_exc()

print("\n" + "=" * 60)
