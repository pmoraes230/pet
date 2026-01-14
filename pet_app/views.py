from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from datetime import date
from django.views.decorators.http import require_http_methods
from . import models
from django.contrib.auth import logout
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import random
import logging

logger = logging.getLogger(__name__)

# Utils imports (se existir)
try:
    from .utils import get_tutor_logado, get_veterinario_logado
except ImportError:
    def get_tutor_logado(request):
        user_id = request.session.get('user_id')
        user_role = request.session.get('user_role')
        if user_role == 'tutor' and user_id:
            return {'id': user_id}
        return None
    
    def get_veterinario_logado(request):
        user_id = request.session.get('user_id')
        user_role = request.session.get('user_role')
        if user_role == 'vet' and user_id:
            return {'id': user_id}
        return None

# ========================================================
# PÁGINA INICIAL E AUTENTICAÇÃO
# ========================================================

def home(request):
    return render(request, 'tela_inicio/index.html')

@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    context = {
        'email': '',
        'role': 'tutor',  # default
        # adicione outros campos se quiser preservar mais dados
    }

    if request.method == 'GET':
        return render(request, 'login/login.html', context)

    # POST
    email = request.POST.get('email', '').strip().lower()
    senha = request.POST.get('senha', '')
    role  = request.POST.get('role', '')

    context.update({
        'email': email,
        'role': role,
    })

    # Validações
    if not email:
        messages.error(request, "O email é obrigatório.")
    if not senha:
        messages.error(request, "A senha é obrigatória.")
    if not role or role not in ['tutor', 'vet']:
        messages.error(request, "Selecione um perfil válido (Tutor ou Veterinário).")

    if messages.get_messages(request):  # já tem erro → early return
        return render(request, 'login/login.html', context)

    user = None
    user_role = None

    try:
        if role == 'tutor':
            tutor = models.Tutor.objects.get(email__iexact=email)
            if check_password(senha, tutor.senha_tutor):
                user = tutor
                user_role = 'tutor'
            else:
                messages.error(request, "Senha incorreta para tutor.")

        elif role == 'vet':
            vet = models.Veterinario.objects.get(email__iexact=email)
            if check_password(senha, vet.senha_veterinario):
                user = vet
                user_role = 'vet'
            else:
                messages.error(request, "Senha incorreta para veterinário.")

    except (models.Tutor.DoesNotExist, models.Veterinario.DoesNotExist):
        messages.error(request, f"Email não encontrado para o perfil selecionado ({role.capitalize()}).")

    except Exception as e:
        messages.error(request, "Erro inesperado ao processar login. Tente novamente mais tarde.")
        # Opcional: logger.error(f"Erro login: {e}")

    if user and user_role:
        # Login via sessão
        request.session['user_id']    = user.id
        request.session['user_role']  = user_role
        request.session['user_nome']  = user.nome_tutor if user_role == 'tutor' else user.nome
        request.session['user_email'] = user.email
        request.session.modified = True

        messages.success(request, f"Bem-vindo(a), {request.session['user_nome']}!")

        if user_role == 'tutor':
            return redirect('tutor_dash')   # confirme o name da URL
        else:
            return redirect('dash_veterinario')

    # Erro → volta ao form com dados preenchidos
    return render(request, 'login/login.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu com sucesso.")
    return redirect('login')

@require_http_methods(["POST"])
def register_view(request):
    # GET não é permitido aqui
    if request.method != 'POST':
        return redirect('login')

    # Dados do formulário
    email = request.POST.get('email', '').strip().lower()
    senha = request.POST.get('senha', '')
    role  = request.POST.get('role', '')
    nome  = request.POST.get('nome', '').strip()
    cpf_cnpj = request.POST.get('cpf_cnpj', '').strip()
    crmv  = request.POST.get('crmv', '').strip()
    data_nascimento_str = request.POST.get('data_nascimento', '').strip()

    # Validações básicas
    if not email:
        messages.error(request, "O email é obrigatório.")
    if not senha:
        messages.error(request, "A senha é obrigatória.")
    if not role or role not in ['tutor', 'vet']:
        messages.error(request, "Selecione um perfil válido (Tutor ou Veterinário).")

    # Validações específicas por role
    if role == 'tutor':
        if not nome:
            messages.error(request, "Nome completo é obrigatório para tutores.")
        if not cpf_cnpj:
            messages.error(request, "CPF é obrigatório para tutores.")
        if not data_nascimento_str:
            messages.error(request, "Data de nascimento é obrigatória para tutores.")

    elif role == 'vet':
        if not nome:
            messages.error(request, "Nome é obrigatório para veterinários.")
        if not cpf_cnpj:
            messages.error(request, "CPF ou CNPJ é obrigatório para veterinários.")
        if not crmv:
            messages.error(request, "CRMV é obrigatório para veterinários.")

    # Verifica se já existem mensagens de erro
    if messages.get_messages(request):
        return render(request, 'login/login.html', {
            'email': email,
            'nome': nome,
            'cpf_cnpj': cpf_cnpj,
            'crmv': crmv,
            'data_nascimento': data_nascimento_str,
            'role': role,
        })

    # Limpar CPF/CNPJ
    cpf_cnpj_limpo = ''.join(filter(str.isdigit, cpf_cnpj))

    # Validar formato CPF/CNPJ
    if len(cpf_cnpj_limpo) not in (11, 14):
        messages.error(request, "CPF deve ter 11 dígitos ou CNPJ 14 dígitos.")
        return render(request, 'login/login.html', {
            'email': email, 'nome': nome, 'cpf_cnpj': cpf_cnpj, 'crmv': crmv,
            'data_nascimento': data_nascimento_str, 'role': role,
        })

    # Converter data de nascimento
    data_nascimento = None
    if data_nascimento_str:
        try:
            data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Data de nascimento inválida (use formato AAAA-MM-DD).")
            return render(request, 'login/login.html', {
                'email': email, 'nome': nome, 'cpf_cnpj': cpf_cnpj, 'crmv': crmv,
                'data_nascimento': data_nascimento_str, 'role': role,
            })

    # Verificar se email já existe
    if models.Tutor.objects.filter(email__iexact=email).exists() or \
       models.Veterinario.objects.filter(email__iexact=email).exists():
        messages.error(request, "Este email já está cadastrado.")
        return render(request, 'login/login.html', {
            'email': email, 'nome': nome, 'cpf_cnpj': cpf_cnpj, 'crmv': crmv,
            'data_nascimento': data_nascimento_str, 'role': role,
        })

    try:
        if role == 'tutor':
            tutor = models.Tutor.objects.create(
                nome_tutor=nome,
                email=email,
                senha_tutor=make_password(senha),
                cpf=cpf_cnpj_limpo,
                data_nascimento=data_nascimento,
                endereco="Endereço não informado",
            )
            # Login automático
            request.session['user_id'] = tutor.id
            request.session['user_role'] = 'tutor'
            request.session['user_nome'] = tutor.nome_tutor
            request.session['user_email'] = tutor.email

            messages.success(request, "Cadastro realizado com sucesso! Bem-vindo(a)!")
            return redirect('dash_tutor')

        elif role == 'vet':
            pf = None
            pj = None

            if len(cpf_cnpj_limpo) == 11:
                pf = models.PessoaFisica.objects.create(
                    cpf=cpf_cnpj_limpo,
                    data_nascimento=data_nascimento or datetime.today().date(),
                    genero="N",
                )
            elif len(cpf_cnpj_limpo) == 14:
                pj = models.PessoaJuridica.objects.create(
                    cnpj=cpf_cnpj_limpo,
                    nome_fantasia=nome,
                    endereco="-",
                    data_criacao=datetime.today().date(),
                )

            vet = models.Veterinario.objects.create(
                nome=nome,
                email=email,
                crmv=int(crmv.replace('/', '').strip() or 0),
                uf_crmv='SP',  # ← TODO: tornar dinâmico no futuro
                senha_veterinario=make_password(senha),
                telefone="0",
                pessoa_fisica=pf,
                pessoa_juridica=pj,
            )

            # Login automático
            request.session['user_id'] = vet.id
            request.session['user_role'] = 'vet'
            request.session['user_nome'] = vet.nome
            request.session['user_email'] = vet.email

            messages.success(request, "Cadastro realizado com sucesso! Bem-vindo(a), Dr(a).!")
            return redirect('vet_dashboard')

    except ValueError as ve:
        messages.error(request, f"Erro de validação: {str(ve)}")
    except Exception as e:
        # Em produção, use logging
        print(f"Erro no cadastro: {str(e)}")
        messages.error(request, "Erro ao criar conta. Tente novamente mais tarde.")

    # Em caso de erro, retorna com os dados preenchidos
    return render(request, 'login/login.html', {
        'email': email,
        'nome': nome,
        'cpf_cnpj': cpf_cnpj,
        'crmv': crmv,
        'data_nascimento': data_nascimento_str,
        'role': role,
    })


# ========================================================
# ÁREA DO TUTOR
# ========================================================

def tutor_dashboard_view(request):
    if request.session.get('user_role') != 'tutor':
        return redirect('login')

    tutor_id = request.session.get('user_id')
    try:
        tutor = models.Tutor.objects.get(id=tutor_id)
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return redirect('login')

    pets = models.Pet.objects.filter(tutor=tutor)
    proxima_consulta = models.Consulta.objects.filter(
        pet__in=pets,
        data_consulta__gte=date.today()
    ).order_by('data_consulta', 'horario_consulta').first()

    historico_recente = models.Consulta.objects.filter(
        pet__in=pets
    ).order_by('-data_consulta', '-horario_consulta')[:5]

    context = {
        'tutor': tutor,
        'pets': pets,
        'proxima_consulta': proxima_consulta,
        'historico_recente': historico_recente,
        'total_pets': pets.count()
    }
    return render(request, 'dash_tutor/dash_tutor.html', context)


def perfil_tutor(request):
    if request.session.get('user_role') != 'tutor':
        return redirect('login')

    tutor = models.Tutor.objects.get(id=request.session['user_id'])
    return render(request, 'tutor_perfil.html', {'tutor': tutor})


def editar_perfil_tutor(request):
    if request.session.get('user_role') != 'tutor':
        return redirect('login')

    tutor = models.Tutor.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        tutor.nome_tutor = request.POST.get('nome')
        tutor.endereco = request.POST.get('endereco')
        if request.FILES.get('image_tutor'):
            tutor.imagem_perfil_tutor = request.FILES['image_tutor']
        tutor.save()
        messages.success(request, "Perfil atualizado!")
        return redirect('perfil_tutor')

    return render(request, 'editar_perfil_tutor.html', {'tutor': tutor})


def meus_pets(request):
    if request.session.get('user_role') != 'tutor':
        return redirect('login')

    tutor = models.Tutor.objects.get(id=request.session['user_id'])
    pets = models.Pet.objects.filter(tutor=tutor)
    return render(request, 'meus_pets.html', {'tutor': tutor, 'pets': pets})


def adicionar_pet(request):
    if request.session.get('user_role') != 'tutor':
        return redirect('login')

    tutor = models.Tutor.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        nome = request.POST.get('nome')
        especie = request.POST.get('especie')
        raca = request.POST.get('raca')
        data_nascimento = request.POST.get('data_nascimento')
        sexo = request.POST.get('sexo')

        prontuario = models.ProntuarioPet.objects.create(
            historico_veterinario="Inicial",
            motivo_consulta="Cadastro",
            avaliacao_geral="-",
            procedimentos="-",
            diagnostico_conslusivo="-",
            observacao="-"
        )

        models.Pet.objects.create(
            nome=nome,
            especie=especie,
            raca=raca,
            data_nascimento=data_nascimento,
            sexo=sexo,
            pelagem="Padrão",
            castrado="Não",
            tutor=tutor
        )
        messages.success(request, "Pet adicionado!")
        return redirect('meus_pets')

    return render(request, 'adicionar_pet.html')


def excluir_pet(request, pet_id):
    if request.session.get('user_role') != 'tutor':
        return redirect('login')

    tutor_id = request.session['user_id']
    pet = models.Pet.objects.filter(id=pet_id, tutor_id=tutor_id).first()

    if pet:
        pet.delete()
        messages.success(request, "Pet removido.")

    return redirect('meus_pets')


# ========================================================
# ÁREA DO VETERINÁRIO
# ========================================================

def vet_dashboard_view(request):
    if request.session.get('user_role') != 'vet':
        return redirect('login')

    vet_id = request.session.get('user_id')
    try:
        veterinario = models.Veterinario.objects.get(id=vet_id)
    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return redirect('login')

    # --- NOVO: BUSCAR NOTIFICAÇÕES DO BANCO ---
    # Pegamos as 5 mais recentes
    notificacoes = models.pet_app_notificacao.objects.filter(veterinario=veterinario).order_by('-data_criacao')[:5]
    # Contamos quantas não foram lidas
    notificacoes_nao_lidas_count = models.pet_app_notificacao.objects.filter(veterinario=veterinario, lida=False).count()
    # ------------------------------------------

    consultas_hoje = models.Consulta.objects.filter(veterinario=veterinario, data_consulta=date.today()).count()
    faturamento = models.Consulta.objects.filter(veterinario=veterinario, data_consulta=date.today()).aggregate(
        Sum('valor_consulta')
    )['valor_consulta__sum'] or 0
    agenda = models.Consulta.objects.filter(veterinario=veterinario, data_consulta=date.today()).select_related('pet').order_by('horario_consulta')

    context = {
        'veterinario': veterinario,
        'consultas_hoje': consultas_hoje,
        'faturamento_dia': faturamento,
        'agenda_hoje': agenda,
        'total_pacientes': models.Pet.objects.count(),
        
        # Enviando para o template:
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas_count': notificacoes_nao_lidas_count,
    }
    return render(request, 'vet_dash.html', context)


# No arquivo pet_app/views.py, por volta da linha 202

def perfil_veterinario(request):
    if request.session.get('user_role') != 'vet':
        return redirect('login')

    veterinario = models.Veterinario.objects.get(id=request.session['user_id'])
    
    # MUDE DE 'veterinario_perfil.html' PARA 'vet_perfil.html'
    return render(request, 'vet_perfil.html', {'veterinario': veterinario})

def editar_perfil_veterinario(request):
    if request.session.get('user_role') != 'vet':
        return redirect('login')

    veterinario = models.Veterinario.objects.get(id=request.session['user_id'])
    return render(request, 'editar_perfil_veterinario.html', {'veterinario': veterinario})

from django.http import JsonResponse

@csrf_exempt
def insert_tutor_ajax(request):
    if request.method == "POST":
        # exemplo simples (ajuste depois conforme sua lógica)
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Método inválido"})



def lista_notificacoes(request):
    if request.session.get('user_role') != 'vet':
        return redirect('login')
    
    vet_id = request.session.get('user_id')
    veterinario = models.Veterinario.objects.get(id=vet_id)
    
    # Busca todas
    todas_notificacoes = models.Notificacao.objects.filter(veterinario=veterinario).order_by('-data_criacao')
    
    return render(request, 'notificacoes_completa.html', {
        'veterinario': veterinario,
        'notificacoes': todas_notificacoes
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from . import models 
import logging

# Adicionei logs para você ver o erro no terminal do VS Code
logger = logging.getLogger(__name__)

def mensagens_view(request):
    """Exibe chat para o Tutor."""
    try:
        tutor_data = get_tutor_logado(request)
        if not tutor_data:
            return redirect('login')

        tutor = models.Tutor.objects.get(id=tutor_data['id'])
        contatos = models.Veterinario.objects.all()

        vet_id = request.GET.get('vet_id')
        mensagens = []
        vet_selecionado = None

        if vet_id:
            vet_selecionado = get_object_or_404(models.Veterinario, id=vet_id)
            mensagens = models.Mensagem.objects.filter(
                tutor=tutor,
                veterinario=vet_selecionado
            ).order_by('DATA_ENVIO')

        return render(request, 'mensagens.html', {
            'tutor': tutor,
            'contatos': contatos,
            'mensagens': mensagens,
            'vet_selecionado': vet_selecionado,
        })
    except Exception as e:
        logger.exception("Erro em mensagens_view")
        return render(request, 'erro.html', {'msg': str(e)})


def enviar_mensagem(request):
    if request.method == 'POST':
        tutor_data = get_tutor_logado(request)
        if not tutor_data:
            return redirect('login')

        tutor = get_object_or_404(models.Tutor, id=tutor_data['id'])
        vet_id = request.POST.get('vet_id')
        texto = request.POST.get('mensagem')

        if texto and vet_id:
            vet = get_object_or_404(models.Veterinario, id=vet_id)
            models.Mensagem.objects.create(
                tutor=tutor,
                veterinario=vet,
                CONTEUDO=texto,
                ENVIADO_POR='TUTOR'
            )
            # Use o nome da URL em vez de path fixo se possível
            return redirect(f'/mensagens/?vet_id={vet_id}')
            
    return redirect('mensagens')

import random
from django.shortcuts import render, redirect
from .models import CodigoRecuperacao

# --- 1. SOLICITAR (VIA LOGIN/ESQUECI SENHA) ---
def solicitar_troca_senha(request):
    if request.method == "POST":
        email_destino = request.POST.get('email', '').strip().lower()
        
        if not email_destino:
            messages.error(request, "Email é obrigatório.")
            return render(request, 'autenticacao/solicitar_troca.html')
        
        # Verifica se existe um Tutor ou Veterinário com este email
        tutor_existe = models.Tutor.objects.filter(email__iexact=email_destino).exists()
        vet_existe = models.Veterinario.objects.filter(email__iexact=email_destino).exists()
        
        if not tutor_existe and not vet_existe:
            messages.error(request, "Email não encontrado no sistema.")
            return render(request, 'autenticacao/solicitar_troca.html')
        
        codigo = str(random.randint(10000, 99999))
        
        # Salva no banco
        CodigoRecuperacao.objects.create(email=email_destino, codigo=codigo)
        
        logger.info(f"Enviando código de recuperação para {email_destino}")
        
        # ENVIA O E-MAIL
        try:
            resultado = send_mail(
                'Código de Segurança - Coração em Patas',
                f'Seu código de recuperação de senha é: {codigo}\n\nEste código é válido por 24 horas.\n\nNão compartilhe com ninguém!',
                settings.EMAIL_HOST_USER,
                [email_destino],
                fail_silently=False,
            )
            logger.info(f"Email enviado com sucesso para {email_destino} (resultado: {resultado})")
            messages.success(request, f"Código enviado para {email_destino}. Verifique seu email.")
        except Exception as e:
            logger.error(f"Erro ao enviar email para {email_destino}: {str(e)}", exc_info=True)
            messages.error(request, f"Erro ao enviar email: {str(e)}")
            return render(request, 'autenticacao/solicitar_troca.html')
        
        request.session['email_recuperacao'] = email_destino
        return redirect('inserir_codigo')
    return render(request, 'autenticacao/solicitar_troca.html')

# --- 2. SOLICITAR (VIA PERFIL/LOGADO) ---
def alterar_senha_logado(request):
    email_do_tutor = request.session.get('user_email') or request.session.get('tutor_email') or request.session.get('email')
    
    if not email_do_tutor and request.user.is_authenticated:
        email_do_tutor = request.user.email

    if not email_do_tutor:
        messages.error(request, "Não foi possível identificar seu email.")
        return redirect('login')

    codigo = str(random.randint(10000, 99999))
    CodigoRecuperacao.objects.create(email=email_do_tutor, codigo=codigo)
    
    try:
        send_mail(
            'Código de Segurança - Coração em Patas',
            f'Seu código de recuperação de senha é: {codigo}\n\nEste código é válido por 24 horas.\n\nNão compartilhe com ninguém!',
            settings.EMAIL_HOST_USER,
            [email_do_tutor],
            fail_silently=False,
        )
        messages.success(request, f"Código enviado para {email_do_tutor}. Verifique seu email.")
    except Exception as e:
        messages.error(request, f"Erro ao enviar email: {str(e)}")
        print(f"ERRO ao enviar email: {e}")
        return render(request, 'autenticacao/solicitar_troca.html')
    
    request.session['email_recuperacao'] = email_do_tutor
    return redirect('inserir_codigo')

# --- 3. TELA DE INSERIR O CÓDIGO (A QUE ESTAVA DANDO ERRO) ---
def inserir_codigo(request):
    if request.method == "POST":
        # Pega os 5 dígitos dos inputs
        codigo_enviado = ""
        for i in range(1, 6):
            digito = request.POST.get(f'digito_{i}', '')
            codigo_enviado += digito
            
        email = request.session.get('email_recuperacao')
        
        # Verifica se o código existe no banco para esse email
        valido = CodigoRecuperacao.objects.filter(email=email, codigo=codigo_enviado).exists()
        
        if valido:
            return redirect('nova_senha')
        else:
            # Você pode adicionar uma mensagem de erro aqui depois
            print("Código Inválido!")
            
    return render(request, 'autenticacao/inserir_codigo.html')

def nova_senha(request):
    if request.method == "POST":
        senha = request.POST.get('senha')
        confirmacao = request.POST.get('confirmacao')
        email = request.session.get('email_recuperacao')
        
        if not email:
            messages.error(request, "Erro: email de recuperação não encontrado.")
            return redirect('solicitar_troca_senha')

        if senha and senha == confirmacao:
            # Tenta localizar um Tutor primeiro
            tutor = models.Tutor.objects.filter(email__iexact=email).first()
            if tutor:
                tutor.senha_tutor = make_password(senha)
                tutor.save()
            else:
                # Se não for tutor, tenta como Veterinário
                vet = models.Veterinario.objects.filter(email__iexact=email).first()
                if vet:
                    vet.senha_veterinario = make_password(senha)
                    vet.save()

            # Se o usuário estava logado, redireciona para o perfil apropriado
            user_role = request.session.get('user_role')
            if user_role == 'tutor' and request.session.get('user_id'):
                messages.success(request, "Senha alterada com sucesso.")
                return redirect('perfil_tutor')
            if user_role == 'vet' and request.session.get('user_id'):
                messages.success(request, "Senha alterada com sucesso.")
                return redirect('perfil_vet')

            # Caso contrário, volta para o login
            messages.success(request, "Senha alterada com sucesso. Faça login com a nova senha.")
            return redirect('login')

        messages.error(request, "As senhas não conferem.")

    return render(request, 'autenticacao/nova_senha.html')
