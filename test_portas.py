#!/usr/bin/env python
"""
Script para testar diferentes portas SMTP do Gmail
"""
import socket

print("=" * 60)
print("TESTE DE PORTAS DISPONÍVEIS")
print("=" * 60)

portas = {
    587: "SMTP com STARTTLS (TLS)",
    465: "SMTP com SSL",
    25: "SMTP padrão (raramente funciona)",
}

host = "smtp.gmail.com"

for porta, descricao in portas.items():
    print(f"\n🔄 Testando porta {porta} ({descricao})...")
    try:
        resultado = socket.create_connection((host, porta), timeout=5)
        resultado.close()
        print(f"   ✅ SUCESSO! Porta {porta} está acessível")
    except socket.timeout:
        print(f"   ❌ TIMEOUT - Porta bloqueada ou não responde")
    except ConnectionRefusedError:
        print(f"   ❌ RECUSADO - Servidor recusou conexão")
    except Exception as e:
        print(f"   ❌ ERRO - {e}")

print("\n" + "=" * 60)
print("RESULTADO:")
print("=" * 60)
print("\nSe a porta 465 funcionou, atualize o .env com:")
print("  EMAIL_PORT=465")
print("  EMAIL_USE_TLS=False")
print("  EMAIL_USE_SSL=True")
print("\nSe a porta 587 funcionou, deixe como está.")
print("=" * 60)
