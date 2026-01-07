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
from .utils import get_tutor_logado, get_veterinario_logado

# ========================================================
# PÁGINA INICIAL E AUTENTICAÇÃO
# ========================================================

def home(request):
    return render(request, 'tela_inicio/index.html')


@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login/login.html')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '')
        role = request.POST.get('role')
        try_both = False
        if not role:
            # fallback: se o campo role não foi enviado (JS desativado), tentamos ambos
            try_both = True

        if not email or not senha:
            messages.error(request, "Email e senha são obrigatórios.")
            return render(request, 'login/login.html')

        if role == "tutor" or try_both:
            try:
                user = models.Tutor.objects.get(email__iexact=email)
                if check_password(senha, user.senha_tutor) or senha == user.senha_tutor:
                    request.session['user_id'] = user.id
                    request.session['user_role'] = 'tutor'
                    request.session['user_nome'] = user.nome_tutor
                    return redirect('tutor_dashboard')
                else:
                    messages.error(request, "Senha incorreta.")
            except models.Tutor.DoesNotExist:
                messages.error(request, "Email de tutor não encontrado.")
        elif role == "vet" or try_both:
            try:
                vet = models.Veterinario.objects.get(email__iexact=email)
                if check_password(senha, vet.senha_veterinario) or senha == vet.senha_veterinario:
                    request.session['user_id'] = vet.id
                    request.session['user_role'] = 'vet'
                    request.session['user_nome'] = vet.nome
                    return redirect('vet_dashboard')
                else:
                    messages.error(request, "Senha incorreta.")
            except models.Veterinario.DoesNotExist:
                messages.error(request, "Email de veterinário não encontrado.")

    # Suporte a chamada via AJAX/JSON para tutor ou vet
    if role == "tutor" or try_both:
        try:
            user = models.Tutor.objects.get(email__iexact=email)
            if hasattr(models.Tutor, 'status_conta') and not models.Tutor.status_conta:
                return JsonResponse({"success": False, "error": "Esta conta está desativada. Entre em contato com o suporte."})
            if check_password(senha, user.senha_tutor):
                request.session['user_id'] = user.id
                request.session['user_role'] = 'tutor'
                request.session['user_email'] = user.email
                request.session['user_nome'] = user.nome_tutor or "Tutor"
                return JsonResponse({"success": True, "redirect": "/tutor_dash/dash_tutor/"})
            else:
                return JsonResponse({"success": False, "error": "Senha incorreta"})
        except models.Tutor.DoesNotExist:
            return JsonResponse({"success": False, "error": "Email não encontrado"})
    elif role == "vet" or try_both:
        try:
            vet = models.Veterinario.objects.get(email__iexact=email)
            if check_password(senha, vet.senha_veterinario):
                request.session['user_id'] = vet.id
                request.session['user_role'] = 'vet'
                request.session['user_email'] = vet.email
                request.session['user_nome'] = vet.nome or "Veterinário"
                return JsonResponse({"success": True, "redirect": "/vet_dash/"})
            else:
                return JsonResponse({"success": False, "error": "Senha incorreta"})
        except models.Veterinario.DoesNotExist:
            return JsonResponse({"success": False, "error": "Email não encontrado"})

    return render(request, 'login/login.html')


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
from . import models  # Certifique-se que o import está assim
from django.contrib import messages # Para avisar erros na tela

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
            url = reverse('mensagens')
            return redirect(f"{url}?vet_id={vet_id}")

    return redirect('mensagens')


def mensagens_vet_view(request):
    """Exibe chat para o Veterinário."""
    try:
        vet_data = get_veterinario_logado(request)
        if not vet_data:
            return redirect('login')

        vet = models.Veterinario.objects.get(id=vet_data['id'])
        contatos = models.Tutor.objects.all()

        tutor_id = request.GET.get('tutor_id')
        mensagens = []
        tutor_selecionado = None

        if tutor_id:
            tutor_selecionado = get_object_or_404(models.Tutor, id=tutor_id)
            mensagens = models.Mensagem.objects.filter(
                tutor=tutor_selecionado,
                veterinario=vet
            ).order_by('DATA_ENVIO')

        return render(request, 'mensagensvet.html', {
            'contatos': contatos,
            'tutor_selecionado': tutor_selecionado,
            'mensagens': mensagens,
            'veterinario': vet,
        })
    except Exception as e:
        logger.exception("Erro em mensagens_vet_view")
        return render(request, 'erro.html', {'msg': str(e)})


def enviar_mensagem_vet(request):
    if request.method == 'POST':
        vet_data = get_veterinario_logado(request)
        if not vet_data:
            return redirect('login')

        vet = get_object_or_404(models.Veterinario, id=vet_data['id'])
        tutor_id = request.POST.get('tutor_id')
        texto = request.POST.get('mensagem')

        if texto and tutor_id:
            tutor = get_object_or_404(models.Tutor, id=tutor_id)
            models.Mensagem.objects.create(
                tutor=tutor,
                veterinario=vet,
                CONTEUDO=texto,
                ENVIADO_POR='VETERINARIO'
            )
            url = reverse('mensagens_vet')
            return redirect(f"{url}?tutor_id={tutor_id}")

    return redirect('mensagens_vet')
    
