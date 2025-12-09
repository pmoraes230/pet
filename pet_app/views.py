import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from MySQLdb import OperationalError, ProgrammingError
from . import models
from .utils import call_procedure  # Apenas se usar para cadastrar tutor via procedure
import traceback
import datetime


# -------------------
# Página inicial
# -------------------
def home(request):
    return render(request, 'tela_inicio/index.html')


# -------------------
# Login
# -------------------
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

    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""
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
                return JsonResponse({"success": True, "redirect": "/vet_dash/"})
            else:
                return JsonResponse({"success": False, "error": "Senha incorreta"})
        except models.Veterinario.DoesNotExist:
            return JsonResponse({"success": False, "error": "Email não encontrado"})
        

    return JsonResponse({"success": False, "error": "Tipo de usuário inválido"})



    
    


# -------------------
# Logout
# -------------------
def logout_view(request):
    request.session.flush()  # Limpa a sessão
    return redirect('login')


# -------------------
# Registro
# -------------------
@csrf_exempt
def register_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)

    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""
    nome = (data.get("nome") or "").strip()
    crmv = (data.get("crmv") or "").strip()
    role = data.get("role")
    data_nascimento = data.get("nascimento")
    cpf = (data.get("cpf") or "").strip()
    cpf_cnpj = (data.get("cpf_cnpj") or "").strip()

    if not email or not senha:
        return JsonResponse({"success": False, "error": "Email e senha são obrigatórios"})

    # -------------------
    # Cadastro do Tutor
    # -------------------
    if role == "tutor":
        if not nome:
            return JsonResponse({"success": False, "error": "Nome é obrigatório"})
        if not cpf or len(cpf) != 11 or not cpf.isdigit():
            return JsonResponse({"success": False, "error": "CPF deve ter 11 dígitos numéricos"})
        if not data_nascimento:
            return JsonResponse({"success": False, "error": "Data de nascimento é obrigatória"})

        senha_hash = make_password(senha)
        try:
            call_procedure('insert_tutor', [
                nome,
                email,
                senha_hash,
                cpf,
                data_nascimento
            ])
        except (OperationalError, ProgrammingError) as e:
            error_msg = str(e)
            if "45000" in error_msg:
                msg = error_msg.split("45000")[-1].strip()
                return JsonResponse({"success": False, "error": msg})
            return JsonResponse({"success": False, "error": "Erro no banco de dados"})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Erro inesperado: {str(e)}"})

        tutor = models.Tutor.objects.get(email=email)
        request.session['user_id'] = tutor.id
        request.session['user_role'] = 'tutor'
        request.session['user_nome'] = tutor.nome_tutor or nome

        return JsonResponse({"success": True, "redirect": "/tutor_dash/dash_tutor/"})

    # -------------------
    # Cadastro do Veterinário
    # -------------------
    elif role == "vet":
        try:
            if not nome or not crmv:
                return JsonResponse({"success": False, "error": "Nome e CRMV são obrigatórios"})

            # Limpar CPF/CNPJ para apenas números
            cpf_cnpj = "".join(filter(str.isdigit, cpf_cnpj))
            if not cpf_cnpj or len(cpf_cnpj) not in [11, 14]:
                return JsonResponse({"success": False, "error": "CPF ou CNPJ inválido"})

            # Verificar duplicidade
            if models.Veterinario.objects.filter(email__iexact=email).exists():
                return JsonResponse({"success": False, "error": "Este email já está cadastrado"})
            if len(cpf_cnpj) == 11 and models.Veterinario.objects.filter(pessoa_fisica__cpf=cpf_cnpj).exists():
                return JsonResponse({"success": False, "error": "Este CPF já está cadastrado"})
            if len(cpf_cnpj) == 14 and models.Veterinario.objects.filter(pessoa_juridica__cnpj=cpf_cnpj).exists():
                return JsonResponse({"success": False, "error": "Este CNPJ já está cadastrado"})

            # Validar CRMV
            try:
                crmv_num = int(crmv.split("/")[0])
                uf = crmv.split("/")[-1].upper()[:2] if "/" in crmv else "SP"
            except ValueError:
                return JsonResponse({"success": False, "error": "CRMV inválido"})

            # Garantir data de nascimento válida
            try:
                data_nascimento_obj = datetime.datetime.strptime(data_nascimento, "%Y-%m-%d").date() if data_nascimento else datetime.date(2000,1,1)
            except Exception:
                data_nascimento_obj = datetime.date(2000,1,1)

            # Criar PessoaFisica (apenas se for CPF)
            pessoa_fisica = None
            if len(cpf_cnpj) == 11:
                pessoa_fisica = models.PessoaFisica.objects.create(
                    cpf=cpf_cnpj,
                    data_nascimento=data_nascimento_obj,
                    genero="N"
                )

            # Criar PessoaJuridica (apenas se for CNPJ)
            pessoa_juridica = None
            if len(cpf_cnpj) == 14:
                pessoa_juridica = models.PessoaJuridica.objects.create(
                    cnpj=cpf_cnpj,
                    nome_fantasia=nome,
                    endereco="Não informado",
                    data_criacao=datetime.date.today()
                )

            # Criar Veterinario
            vet = models.Veterinario.objects.create(
                nome=nome,
                email=email,
                crmv=crmv_num,
                uf_crmv=uf,
                senha_veterinario=make_password(senha),
                telefone="0",
                pessoa_fisica=pessoa_fisica,
                pessoa_juridica=pessoa_juridica
            )

            # Criar sessão
            request.session['user_id'] = vet.id
            request.session['user_role'] = 'vet'
            request.session['user_nome'] = vet.nome

            return JsonResponse({"success": True, "redirect": "/dashboard/vet/"})

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"success": False, "error": f"Erro ao salvar veterinário: {str(e)}"})


@csrf_exempt
def insert_tutor_ajax(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        cpf = request.POST.get("cpf")
        data_nascimento = request.POST.get("data_nascimento")
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Método inválido"}, status=400)

def vet_dashboard_view(request):
    # Aqui você renderiza o template do dashboard do veterinário
    return render(request, "vet_dashboard.html")


def tutor_dashboard_view(request):
    # Aqui você renderiza o template do dashboard do tutor
    return render(request, "tutor_dashboard.html")
