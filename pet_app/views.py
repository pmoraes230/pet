# pet_app/views.py

import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from . import models


def home(request):
    return render(request, 'tela_inicio/index.html')


# ========================
# 1. LOGIN (APENAS LOGIN)
# ========================
@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login/login.html')

    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)

    email = data.get("email", "").strip().lower()
    senha = data.get("senha", "")
    role = data.get("role")

    if not email or not senha or not role:
        return JsonResponse({"success": False, "error": "Email, senha e tipo de usuário são obrigatórios"})

    # LOGIN TUTOR
    if role == "tutor":
        try:
            tutor = models.Tutor.objects.get(email__iexact=email)
            if check_password(senha, tutor.senha_tutor):
                request.session['user_id'] = tutor.id
                request.session['user_role'] = 'tutor'
                request.session['user_nome'] = tutor.nome_tutor
                return JsonResponse({"success": True, "redirect": "/tutor_dash/dash_tutor/"})
            else:
                return JsonResponse({"success": False, "error": "Senha incorreta"})
        except models.Tutor.DoesNotExist:
            return JsonResponse({"success": False, "error": "Email não encontrado. Cadastre-se primeiro."})

    # LOGIN VETERINÁRIO
    elif role == "vet":
        try:
            vet = models.Veterinario.objects.get(email__iexact=email)
            if check_password(senha, vet.senha_veterinario):
                request.session['user_id'] = vet.id
                request.session['user_role'] = 'vet'
                request.session['user_nome'] = vet.nome
                return JsonResponse({"success": True, "redirect": "/dashboard/vet/"})
            else:
                return JsonResponse({"success": False, "error": "Senha incorreta"})
        except models.Veterinario.DoesNotExist:
            return JsonResponse({"success": False, "error": "Email não encontrado"})

    return JsonResponse({"success": False, "error": "Tipo de usuário inválido"})


# ========================
# 2. CADASTRO (CORRIGIDO!)
# ========================
@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)

    email = data.get("email", "").strip().lower()
    senha = data.get("senha", "")
    nome = data.get("nome", "").strip()
    cpf = data.get("cpf", "").strip()
    nascimento = data.get("nascimento")  # frontend manda "nascimento"
    crmv = data.get("crmv", "").strip()
    role = data.get("role")

    if not all([email, senha, role]):
        return JsonResponse({"success": False, "error": "Email, senha e role são obrigatórios"})

# CADASTRO DE TUTOR
    if role == "tutor":
            if not nome:
                return JsonResponse({"success": False, "error": "Nome é obrigatório"})
            if not cpf or len(cpf) != 11 or not cpf.isdigit():
                return JsonResponse({"success": False, "error": "CPF deve ter 11 dígitos numéricos"})
            if not nascimento:
                return JsonResponse({"success": False, "error": "Data de nascimento é obrigatória"})

            # Converte a data corretamente
            try:
                if "/" in nascimento:
                    nascimento = datetime.strptime(nascimento, "%d/%m/%Y").date()
                else:
                    nascimento = datetime.strptime(nascimento, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"success": False, "error": "Data inválida. Use DD/MM/AAAA ou AAAA-MM-DD"})

            senha_hash = make_password(senha)

            # Verifica duplicidade ANTES de tentar salvar
            if models.Tutor.objects.filter(email__iexact=email).exists():
                return JsonResponse({"success": False, "error": "Este email já está cadastrado"})
            if models.Tutor.objects.filter(cpf=cpf).exists():
                return JsonResponse({"success": False, "error": "Este CPF já está cadastrado"})

            try:
                tutor = models.Tutor(
                    nome_tutor=nome,
                    cpf=cpf,
                    email=email,
                    endereco="Sem endereço",
                    data_nascimento=nascimento,
                    senha_tutor=senha_hash,
                    imagem_perfil_tutor=None,
                )
                tutor.full_clean()  # valida tudo
                tutor.save()

                # Login automático
                request.session['user_id'] = tutor.id
                request.session['user_role'] = 'tutor'
                request.session['user_nome'] = tutor.nome_tutor

                return JsonResponse({"success": True, "redirect": "/tutor_dash/dash_tutor/"})

            except Exception as e:
                return JsonResponse({"success": False, "error": f"Erro ao salvar: {str(e)}"})

    # CADASTRO DE VETERINÁRIO
    elif role == "vet":
        if not nome or not crmv:
            return JsonResponse({"success": False, "error": "Nome e CRMV são obrigatórios"})

        if models.Veterinario.objects.filter(email__iexact=email).exists():
            return JsonResponse({"success": False, "error": "Email já cadastrado"})

        try:
            partes = crmv.replace(" ", "").split("/")
            crmv_num = int(partes[0])
            uf = partes[1].upper()[:2] if len(partes) > 1 else "SP"
        except:
            return JsonResponse({"success": False, "error": "CRMV inválido (ex: 12345/SP)"})

        vet = models.Veterinario(
            nome=nome,
            email=email,
            crmv=crmv_num,
            uf_crmv=uf,
            senha_veterinario=make_password(senha),
            telefone="00000000000"
        )
        vet.save()

        request.session['user_id'] = vet.id
        request.session['user_role'] = 'vet'
        request.session['user_nome'] = vet.nome
        return JsonResponse({"success": True, "redirect": "/dashboard/vet/"})

    return JsonResponse({"success": False, "error": "Role inválido"})


# ========================
# LOGOUT
# ========================
def logout_view(request):
    logout(request)
    return redirect('login')