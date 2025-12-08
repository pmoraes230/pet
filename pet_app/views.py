import json
from MySQLdb import OperationalError, ProgrammingError
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .utils import call_procedure
from django.contrib import messages
from . import models
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import rotate_token

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
                return JsonResponse({"success": True, "redirect": "/tutor_dash/dash_tutor/"})
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

def logout_view(request):
    logout(request)
    return redirect('login')

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
        # Validações básicas no Python (sempre bom ter dupla camada)
        if not nome:
            return JsonResponse({"success": False, "error": "Nome é obrigatório"})
        if not cpf or len(cpf) != 11 or not cpf.isdigit():
            return JsonResponse({"success": False, "error": "CPF deve ter 11 dígitos numéricos"})
        if not data_nascimento:
            return JsonResponse({"success": False, "error": "Data de nascimento é obrigatória"})

        senha_hash = make_password(senha)
        try:
            # CHAMADA DA PROCEDURE USANDO SUA FUNÇÃO
            call_procedure('insert_tutor', [
            nome,           # nome_completo
            email,          # email
            senha_hash,     # senha
            cpf,            # cpf
            data_nascimento # data_nascimento
            ])

        except (OperationalError, ProgrammingError) as e:
            # Captura erros do MySQL (ex: SIGNAL SQLSTATE)
            error_msg = str(e)

            # Extrai a mensagem personalizada do SIGNAL
            if "45000" in error_msg:
                # Exemplo de erro: "1048: O nome do tutor é obrigatório"
                msg = error_msg.split("45000")[-1].strip()
                if "O nome do tutor é obrigatório" in msg:
                    return JsonResponse({"success": False, "error": "Nome é obrigatório"})
                if "CPF deve conter exatamente 11 dígitos" in msg:
                    return JsonResponse({"success": False, "error": "CPF inválido"})
                if "Email já cadastrado" in msg:
                    return JsonResponse({"success": False, "error": "Este email já está cadastrado"})
                if "CPF já cadastrado" in msg:
                    return JsonResponse({"success": False, "error": "Este CPF já está cadastrado"})
                # Qualquer outro erro da procedure
                return JsonResponse({"success": False, "error": msg})

            return JsonResponse({"success": False, "error": "Erro no banco de dados"})

        except Exception as e:
            return JsonResponse({"success": False, "error": f"Erro inesperado: {str(e)}"})

        # Login automático após sucesso
        tutor = models.Tutor.objects.get(email=email)
        request.session['user_id'] = tutor.id
        request.session['user_role'] = 'tutor'
        request.session['user_nome'] = tutor.nome_tutor or nome

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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # se for chamado via JS/AJAX
def insert_tutor_ajax(request):
    if request.method == "POST":
        # Aqui você pega os dados do request.POST e salva no banco
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        cpf = request.POST.get("cpf")
        data_nascimento = request.POST.get("data_nascimento")
        # TODO: salvar no banco
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Método inválido"}, status=400)
