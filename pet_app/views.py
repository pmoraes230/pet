from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from datetime import date
from . import models
from django.contrib.auth import logout
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import random
import logging
# pet_app/views.py
from .models import Mensagem
from .models import Pet, Veterinario, Consulta, Vacina # Verifique se os nomes dos modelos estão corretos
from django.contrib import messages
from pet_app import models as pet_models 
from datetime import datetime, date, timedelta


from django.shortcuts import render, redirect
# ADICIONE ESTA LINHA ABAIXO:
from .models import Notificacao, Consulta, Pet # E outros modelos que você usar

logger = logging.getLogger(__name__)

# Utils imports (se existir)
try:
    from .utils import get_tutor_logado, get_veterinario_logado
except ImportError:
    def get_tutor_logado(request):
        user_id = request.session.get('user_id')
        user_role = request.session.get('user_role')
        if user_role == 'tutor' and user_id:
            try:
                # Retornamos o objeto completo para facilitar o uso nas views
                return pet_models.Tutor.objects.get(id=user_id)
            except pet_models.Tutor.DoesNotExist:
                return None
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


@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login/login.html')

    # Sempre responder com JSON no POST
    response_data = {"success": False, "error": "Erro desconhecido"}

    try:
        if request.method == 'POST':
            email = request.POST.get('email', '').strip().lower()
            senha = request.POST.get('senha', '')
            role = request.POST.get('role', '')

            if not email or not senha:
                response_data["error"] = "Email e senha são obrigatórios."
                return JsonResponse(response_data, status=400)

            if role == "tutor":
                try:
                    user = models.Tutor.objects.get(email__iexact=email)
                    if check_password(senha, user.senha_tutor):
                        request.session['user_id'] = user.id
                        request.session['user_role'] = 'tutor'
                        request.session['user_nome'] = user.nome_tutor or ""
                        request.session['user_email'] = user.email
                        response_data["success"] = True
                        response_data["redirect"] = "/tutor_dash/dash_tutor/"
                    else:
                        response_data["error"] = "Senha incorreta."
                except models.Tutor.DoesNotExist:
                    response_data["error"] = "Email de tutor não encontrado."

            elif role == "vet":
                try:
                    vet = models.Veterinario.objects.get(email__iexact=email)
                    if check_password(senha, vet.senha_veterinario):
                        request.session['user_id'] = vet.id
                        request.session['user_role'] = 'vet'
                        request.session['user_nome'] = vet.nome or ""
                        response_data["success"] = True
                        response_data["redirect"] = "/vet_dash/"
                    else:
                        response_data["error"] = "Senha incorreta."
                except models.Veterinario.DoesNotExist:
                    response_data["error"] = "Email de veterinário não encontrado."

            else:
                response_data["error"] = "Tipo de usuário inválido."

    except Exception as e:
        # Captura qualquer erro inesperado (útil em produção)
        import traceback
        print("Erro inesperado no login:", traceback.format_exc())
        response_data["error"] = "Erro interno no servidor. Tente novamente mais tarde."

    # Define status apropriado
    status_code = 200 if response_data["success"] else 400
    return JsonResponse(response_data, status=status_code)

def logout_view(request):
    logout(request)
    return redirect('login')


@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return redirect('login')

    email = request.POST.get('email', '').strip().lower()
    senha = request.POST.get('senha', '')
    nome = request.POST.get('nome', '').strip()
    role = request.POST.get('role')
    crmv = request.POST.get('crmv', '').strip()
    data_nascimento = request.POST.get('data_nascimento')
    cpf_cnpj = request.POST.get('cpf_cnpj', '').strip()

    if not email or not senha:
        messages.error(request, "Dados incompletos.")
        return render(request, 'login/login.html')

    if role == "tutor":
        try:
            cpf_limpo = "".join(filter(str.isdigit, cpf_cnpj))
            tutor = models.Tutor.objects.create(
                nome_tutor=nome,
                email=email,
                senha_tutor=make_password(senha),
                cpf=cpf_limpo,
                data_nascimento=data_nascimento,
                endereco="Endereço não informado"
            )

            request.session['user_id'] = tutor.id
            request.session['user_role'] = 'tutor'
            request.session['user_nome'] = tutor.nome_tutor
            return redirect('tutor_dashboard')

        except Exception as e:
            print(e)
            messages.error(request, "Erro ao cadastrar tutor.")
            return render(request, 'login/login.html')

    elif role == "vet":
        try:
            if models.Veterinario.objects.filter(email__iexact=email).exists():
                messages.error(request, "Email já cadastrado.")
                return render(request, 'login/login.html')

            cpf_cnpj_limpo = "".join(filter(str.isdigit, cpf_cnpj))
            pf, pj = None, None
            if len(cpf_cnpj_limpo) == 11:
                pf = models.PessoaFisica.objects.create(cpf=cpf_cnpj_limpo, data_nascimento=date.today(), genero="N")
            elif len(cpf_cnpj_limpo) == 14:
                pj = models.PessoaJuridica.objects.create(cnpj=cpf_cnpj_limpo, nome_fantasia=nome, endereco="-", data_criacao=date.today())

            vet = models.Veterinario.objects.create(
                nome=nome,
                email=email,
                crmv=int(crmv.split('/')[0]) if crmv else 0,
                uf_crmv='SP',
                senha_veterinario=make_password(senha),
                telefone="0",
                pessoa_fisica=pf,
                pessoa_juridica=pj
            )
            request.session['user_id'] = vet.id
            request.session['user_role'] = 'vet'
            request.session['user_nome'] = vet.nome
            return redirect('vet_dashboard')

        except Exception as e:
            print(e)
            messages.error(request, "Erro ao cadastrar veterinário.")
            return render(request, 'login/login.html')

    return redirect('login')


# ========================================================
# ÁREA DO TUTOR
# ========================================================

def tutor_dashboard_view(request):
    tutor_data = get_tutor_logado(request) # tutor_data aqui é um dicionário
    if not tutor_data:
        request.session.flush()
        return redirect('login')

    # CORREÇÃO AQUI: 
    # Usamos tutor_id (com o _id no final) e passamos apenas o número do ID
    pets = pet_models.Pet.objects.filter(tutor_id=tutor_data['id'])
    
    # O restante do código continua igual
    proxima_consulta = pet_models.Consulta.objects.filter(
        pet__in=pets,
        data_consulta__gte=date.today()
    ).order_by('data_consulta', 'horario_consulta').first()

    historico_recente = pet_models.Consulta.objects.filter(
        pet__in=pets
    ).order_by('-data_consulta', '-horario_consulta')[:5]

    context = {
        'tutor': tutor_data, # Passa o dicionário para o template
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
            TUTOR=tutor
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
    notificacoes = models.Notificacao.objects.filter(veterinario=veterinario).order_by('-data_criacao')[:5]
    # Contamos quantas não foram lidas
    notificacoes_nao_lidas_count = models.Notificacao.objects.filter(veterinario=veterinario, lida=False).count()
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
    try:
        tutor_data = get_tutor_logado(request)
        if not tutor_data:
            return redirect('login')

        # Busca o objeto do tutor logado
        tutor = models.Tutor.objects.get(id=tutor_data['id']) 
        contatos = models.Veterinario.objects.all()

        vet_id = request.GET.get('vet_id')
        mensagens = []
        vet_selecionado = None

        if vet_id:
            vet_selecionado = get_object_or_404(models.Veterinario, id=vet_id)
            
            # CORREÇÃO AQUI:
            # O campo do banco é TUTOR (maiúsculo)
            # A sua variável lá em cima é tutor (minúsculo)
            mensagens = Mensagem.objects.filter(
                TUTOR=tutor,               # Variável da linha 7
                VETERINARIO=vet_selecionado # Variável da linha 15
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
        # Tenta pegar o tutor ou o veterinário logado
        data_tutor = get_tutor_logado(request)
        data_vet = get_veterinario_logado(request)
        
        texto = request.POST.get('mensagem')
        
        if data_tutor:
            vet_id = request.POST.get('vet_id')
            # CORREÇÃO: Usar nomes MAIÚSCULOS conforme o seu Model
            models.Mensagem.objects.create(
                TUTOR_id=data_tutor['id'], # Antes era tutor=
                VETERINARIO_id=vet_id,     # Antes era veterinario=
                CONTEUDO=texto,            # Antes era conteudo=
                ENVIADO_POR='TUTOR'        # Antes era enviado_por=
            )
            return redirect(f'/mensagens/?vet_id={vet_id}')

        elif data_vet:
            tutor_id = request.POST.get('tutor_id')
            # CORREÇÃO: Usar nomes MAIÚSCULOS conforme o seu Model
            models.Mensagem.objects.create(
                VETERINARIO_id=data_vet['id'],
                TUTOR_id=tutor_id,
                CONTEUDO=texto,
                ENVIADO_POR='VETERINARIO'
            )
            return redirect(f'/mensagens_vet/?tutor_id={tutor_id}')

    return redirect('home')

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


def historico_notificacao(request):
    # 1. Tenta pegar os dados usando suas funções de Utils
    tutor_data = get_tutor_logado(request)
    vet_data = get_veterinario_logado(request)

    # 2. Verifica quem está logado
    if tutor_data:
        user_id = tutor_data['id']
        # Filtra por tutor_id (minúsculo conforme seu model Notificacao)
        notificacoes = Notificacao.objects.filter(tutor_id=user_id).order_by('-data_criacao')
        user_tipo = 'tutor'
    elif vet_data:
        user_id = vet_data['id']
        # Filtra por veterinario_id (minúsculo conforme seu model Notificacao)
        notificacoes = Notificacao.objects.filter(veterinario_id=user_id).order_by('-data_criacao')
        user_tipo = 'vet'
    else:
        # Se nenhum dos dois estiver logado, expulsa
        return redirect('login') 

    # Marca como lidas
    notificacoes.filter(lida=False).update(lida=True)
    
    return render(request, 'notificacoes/notificacoes_history.html', {
        'notificacoes': notificacoes,
        'user_tipo': user_tipo
    })

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Mensagem, Notificacao

def mensagens_view_vet(request):
    """Exibe o chat para o Veterinário."""
    try:
        user_id = request.session.get('user_id')
        user_role = request.session.get('user_role')

        if not user_id or user_role != 'vet':
            return redirect('login')

        vet_logado = get_object_or_404(models.Veterinario, id=user_id)
        contatos_tutores = models.Tutor.objects.all()

        tutor_id = request.GET.get('tutor_id')
        mensagens = []
        tutor_selecionado = None

        if tutor_id:
            tutor_selecionado = get_object_or_404(models.Tutor, id=tutor_id)
            
            # ESTA PARTE PRECISA ESTAR IDENTADA (DENTRO DO IF)
            mensagens = Mensagem.objects.filter(
                TUTOR=tutor_selecionado, 
                VETERINARIO=vet_logado
            ).order_by('DATA_ENVIO')

        # O render fica fora do IF para carregar a página mesmo sem chat aberto
        return render(request, 'mensagensvet.html', { 
            'vet': vet_logado,
            'contatos': contatos_tutores,
            'mensagens': mensagens,
            'tutor_selecionado': tutor_selecionado,
        })
        
    except Exception as e:
        print(f"Erro em mensagens_view_vet: {e}")
        return render(request, 'erro.html', {'msg': str(e)})

def historico_notificacao_vet(request):
    """Exibe o histórico de notificações para o Veterinário."""
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')

    if not user_id or user_role != 'vet':
        return redirect('login') 

    # BUSCA O VETERINÁRIO (Obrigatório para o Header funcionar)
    veterinario = get_object_or_404(models.Veterinario, id=user_id)
    
    # Busca as notificações
    notificacoes = models.Notificacao.objects.filter(veterinario_id=user_id).order_by('-data_criacao')
    
    # Marca como lidas
    notificacoes.filter(lida=False).update(lida=True)
    
    # IMPORTANTE: Removi o "notificacoes/" do caminho porque seu arquivo está solto na pasta templates
    return render(request, 'notificacoes_history_vet.html', {
        'notificacoes': notificacoes,
        'veterinario': veterinario,  # Enviando o objeto para o Header
        'user_role': user_role
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Consulta, Vacina, Pet, Veterinario, Tutor
from datetime import datetime, timedelta

@login_required
def agenda_tutor(request):
    # 1. Identificar o Tutor logado (ajuste conforme seu modelo de User/Tutor)
    tutor = get_object_or_404(Tutor, usuario=request.user)
    
    # 2. Lógica do Calendário Strip
    data_str = request.GET.get('data')
    if data_str:
        data_atual = datetime.strptime(data_str, '%Y-%m-%d').date()
    else:
        data_atual = datetime.now().date()

    # Calcular o início da semana (segunda-feira)
    inicio_semana = data_atual - timedelta(days=data_atual.weekday())
    
    dias_semana = []
    nomes_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        dias_semana.append({
            'nome': nomes_dias[i],
            'num': dia.day,
            'data_completa': dia.strftime('%Y-%m-%d'),
            'hoje': dia == datetime.now().date(),
            'selecionado': dia == data_atual
        })

    # 3. Buscar Dados para a Lista
    # Filtramos consultas e vacinas apenas dos pets que pertencem a este tutor
    consultas = Consulta.objects.filter(
        pet__tutor=tutor, 
        data_consulta__range=[inicio_semana, inicio_semana + timedelta(days=6)]
    ).order_by('data_consulta', 'horario_consulta')

    vacinas = Vacina.objects.filter(
        pet__tutor=tutor,
        data_aplicacao__range=[inicio_semana, inicio_semana + timedelta(days=6)]
    ).order_by('data_aplicacao')

    # 4. Dados para o Modal de Agendamento
    pets = Pet.objects.filter(tutor=tutor)
    veterinarios = Veterinario.objects.all()

    context = {
        'consultas': consultas,
        'vacinas': vacinas,
        'dias_semana': dias_semana,
        'mes_atual': data_atual.strftime('%B'), # Pode precisar de tradução para PT-BR
        'ano_atual': data_atual.year,
        'data_anterior': (inicio_semana - timedelta(days=7)).strftime('%Y-%m-%d'),
        'data_proxima': (inicio_semana + timedelta(days=7)).strftime('%Y-%m-%d'),
        'pets': pets,
        'veterinarios': veterinarios,
    }

    return render(request, 'agenda_tutor.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Pet, Veterinario, Consulta, Vacina # Verifique se os nomes dos modelos estão corretos
from django.contrib import messages

# ... suas outras views ...

