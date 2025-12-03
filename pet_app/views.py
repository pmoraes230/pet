import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from . import models

# Create your views here.
def home(request):
    return render(request, 'tela_inicio/index.html')

@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login/login.html')
    
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)

    email = data.get("email", "").strip().lower()
    senha = data.get("senha", "")
    role = data.get("role")  # 'tutor' ou 'vet'

    if not email or not senha:
        return JsonResponse({"success": False, "error": "Email e senha obrigatórios"})

    if role == "tutor":
        try:
            user = models.Tutor.objects.get(email__iexact=email)
            if check_password(senha, user.senha_tutor):
                request.session['user_id'] = user.id
                request.session['user_role'] = 'tutor'
                request.session['user_nome'] = user.nome_tutor or "Tutor"
                return JsonResponse({"success": True, "redirect": "/dashboard/tutor/"})
            else:
                return JsonResponse({"success": False, "error": "Senha incorreta"})
        except models.Tutor.DoesNotExist:
            return JsonResponse({"success": False, "error": "Email não encontrado"})

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

@csrf_exempt
def register_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)

    email = data.get("email", "").strip().lower()
    senha = data.get("senha", "")
    nome = data.get("nome", "").strip()
    crmv = data.get("crmv", "").strip()
    role = data.get("role")
    data_nascimento = data.get("nascimento")
    cpf = data.get("cpf")

    if not email or not senha:
        return JsonResponse({"success": False, "error": "Email e senha são obrigatórios"})

    if role == "tutor":
        if models.Tutor.objects.filter(email__iexact=email).exists():
            return JsonResponse({"success": False, "error": "Este email já está cadastrado"})

        tutor = models.Tutor(
            nome_tutor=nome or email.split("@")[0],
            email=email,
            data_nascimento=data_nascimento,
            cpf=cpf,
            senha_tutor=make_password(senha)
        )
        tutor.save()

        # Login automático após cadastro
        request.session['user_id'] = tutor.id
        request.session['user_role'] = 'tutor'
        request.session['user_nome'] = tutor.nome_tutor

        return JsonResponse({"success": True, "redirect": "/tutor_dash/dash_tutor/"})

    elif role == "vet":
        if not nome or not crmv:
            return JsonResponse({"success": False, "error": "Nome e CRMV são obrigatórios"})

        if models.Veterinario.objects.filter(email__iexact=email).exists():
            return JsonResponse({"success": False, "error": "Este email já está cadastrado"})

        try:
            crmv_num = int(crmv.split("/")[0]) if "/" in crmv else int(crmv)
            uf = crmv.split("/")[-1].upper()[:2] if "/" in crmv else "SP"
        except ValueError:
            return JsonResponse({"success": False, "error": "CRMV inválido"})

        vet = models.Veterinario(
            nome=nome,
            email=email,
            crmv=crmv_num,
            uf_crmv=uf,
            senha_veterinario=make_password(senha),
            telefone=0
        )
        vet.save()

        request.session['user_id'] = vet.id
        request.session['user_role'] = 'vet'
        request.session['user_nome'] = vet.nome

        return JsonResponse({"success": True, "redirect": "/dashboard/vet/"})

    return JsonResponse({"success": False, "error": "Tipo de usuário inválido"})