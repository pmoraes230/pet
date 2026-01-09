from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required  # se usar no futuro
from pet_app import models
from pet_app.utils import get_tutor_logado, get_veterinario_logado
from django.urls import reverse
import json
from datetime import date, timedelta, datetime

# Create your views here.
def tutor_dashboard_view(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
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


# ========================================================
# PERFIL DO TUTOR
# ========================================================

def perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])

    return render(request, 'edit_tutor/tutor_perfil.html', {
        'tutor': tutor,
        # 'contatos': contatos,  # Descomente quando o modelo existir
    })


def editar_perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    # contatos = models.ContatoTutor.objects.filter(id_tutor=tutor).order_by('-data_cadastro')

    if request.method == "POST":
        # Atualiza dados do tutor
        tutor.nome_tutor = request.POST.get('nome_tutor')
        tutor.cpf = request.POST.get('cpf')
        tutor.data_nascimento = request.POST.get('data_nascimento')
        tutor.endereco = request.POST.get('endereco')
        imagem_tutor = request.FILES.get('image_tutor')
        if imagem_tutor:
            tutor.imagem_perfil_tutor = imagem_tutor
        tutor.save()

        # Processa contatos
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')
        contato_ids = request.POST.getlist('contato_id')

        # Deleta todos e recria (simples e seguro)
        # models.ContatoTutor.objects.filter(id_tutor=tutor.id).delete()

        for i in range(len(tipos)):
            if ddds[i].strip() and numeros[i].strip():
                models.ContatoTutor.objects.create(
                    id_tutor=tutor,          
                    tipo_contato=tipos[i],
                    ddd=ddds[i],
                    numero=numeros[i]
                )

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('perfil_tutor')

    context = {
        'tutor': tutor,
        # 'contatos': contatos,
    }
    return render(request, 'edit_tutor/editar_perfil.html', context)

def config_tutor(request):
    tutor_data = get_tutor_logado(request)

    if not tutor_data:
        return redirect('login')
    
    try:
        tutor = models.Tutor.objects.prefetch_related('pet_set').get(id=tutor_data['id'])
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return redirect('login')
    
    context = {
        'tutor': tutor,
        'tutor_data': tutor_data
    }
    return render(request, 'edit_tutor/configuracoes_tutor.html', context)

def desativar_conta(request):
    if request.method != "POST":
        return redirect('configuracoes_tutor')

    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    data_url = request.GET.get('data')
    if data_url:
        try:
            hoje_referencia = datetime.strptime(data_url, '%Y-%m-%d').date()
        except ValueError:
            hoje_referencia = date.today()
    else:
        hoje_referencia = date.today()

    segunda_da_semana = hoje_referencia - timedelta(days=hoje_referencia.weekday())
    
    data_semana_anterior = segunda_da_semana - timedelta(days=7)
    data_semana_proxima = segunda_da_semana + timedelta(days=7)

    dias_semana = []
    nomes_curtos = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']
    hoje_real = date.today()
    
    for i in range(7):
        dia_iterado = segunda_da_semana + timedelta(days=i)
        dias_semana.append({
            'nome': nomes_curtos[i],
            'num': dia_iterado.day,
            'hoje': dia_iterado == hoje_real,
            'data_full': dia_iterado
        })

    fim_da_semana = segunda_da_semana + timedelta(days=6)
    vacinas = models.Vacina.objects.filter(pet__in=pets, data_aplicacao__range=[segunda_da_semana, fim_da_semana])
    consultas = models.Consulta.objects.filter(pet__in=pets, data_consulta__range=[segunda_da_semana, fim_da_semana])

    meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho',
             7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}

    context = {
        'tutor': tutor,
        'dias_semana': dias_semana,
        'vacinas': vacinas,
        'consultas': consultas,
        'mes_atual': meses[segunda_da_semana.month],
        'ano_atual': segunda_da_semana.year,
        'data_anterior': data_semana_anterior.strftime('%Y-%m-%d'),
        'data_proxima': data_semana_proxima.strftime('%Y-%m-%d'),
    }
    return render(request, 'agendamentos.html', context)
    # Removido o return duplicado

def meus_pets(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    return render(request, 'meus_pets.html', {
        'tutor': tutor,
        'pets': pets
    })

def adicionar_pet(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.filter(id=tutor_data['id']).first()
    if not tutor:
        messages.error(request, "Sessão expirada. Faça login novamente.")
        return redirect('login')

    if request.method == "POST":
        models.Pet.objects.create(
            nome=request.POST.get('nome'),
            especie=request.POST.get('especie'),
            raca=request.POST.get('raca'),
            data_nascimento=request.POST.get('data_nascimento'),
            sexo=request.POST.get('sexo'),
            pelagem=request.POST.get('pelagem', 'Não informada'),
            castrado=request.POST.get('castrado', 'Não'),
            tutor=tutor
        )

        messages.success(request, "Pet cadastrado com sucesso!")
        return redirect('meus_pets')

    return render(request, 'form_pet.html', {'tutor': tutor})

def excluir_pet(request, pet_id):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pet = models.Pet.objects.filter(id=pet_id, tutor=tutor).first()

    if pet:
        pet.delete()
        messages.success(request, "Pet removido com sucesso!")
    else:
        messages.error(request, "Pet não encontrado.")

    return redirect('meus_pets')


def detalhe_pet(request, pet_id):
    pet = get_object_or_404(models.Pet, id=pet_id)

    if request.method == "POST":
        pet.nome = request.POST.get('nome')
        pet.especie = request.POST.get('especie')
        pet.raca = request.POST.get('raca')
        pet.sexo = request.POST.get('sexo')
        pet.pelagem = request.POST.get('pelagem')
        pet.castrado = request.POST.get('castrado')
        pet.peso = request.POST.get('peso')
        pet.descricao = request.POST.get('descricao')
        pet.personalidade = request.POST.get('personalidade')

        if 'imagem' in request.FILES:
            pet.imagem = request.FILES['imagem']

        pet.save()
        return redirect('detalhe_pet', pet_id=pet.id)

    list_personalidades = pet.personalidade.split(',') if pet.personalidade else []

    proxima_consulta = models.Consulta.objects.filter(
        pet=pet, 
        data_consulta__gte=date.today()
    ).order_by('data_consulta').first()

    # CORREÇÃO: Vacina já está importada no topo
    vacinas = models.Vacina.objects.filter(pet=pet).order_by('-data_aplicacao')

    context = {
        'pet': pet,
        'list_personalidades': list_personalidades,
        'proxima_consulta': proxima_consulta,
        'vacinas': vacinas,
    }
    return render(request, 'detalhe_pet.html', context)


# ========================================================
# MEDICAMENTOS / AGENDAMENTOS
# ========================================================

def medicamentos_view(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    hoje = date.today()
    atendimentos_hoje = models.Consulta.objects.filter(
        pet__in=pets,
        data_consulta=hoje
    ).exclude(tratamento__isnull=True).exclude(tratamento='')

    meds_manha = [m for m in atendimentos_hoje if m.horario_consulta and m.horario_consulta.hour < 12]
    meds_tarde = [m for m in atendimentos_hoje if m.horario_consulta and 12 <= m.horario_consulta.hour < 18]
    meds_noite = [m for m in atendimentos_hoje if m.horario_consulta and m.horario_consulta.hour >= 18]

    tratamentos_ativos = models.Consulta.objects.filter(
        pet__in=pets,
        data_consulta__gte=hoje
    ).exclude(tratamento__isnull=True).exclude(tratamento='').order_by('data_consulta')

    context = {
        'tutor': tutor,
        'meds_manha': meds_manha,
        'meds_tarde': meds_tarde,
        'meds_noite': meds_noite,
        'tratamentos_ativos': tratamentos_ativos,
    }
    return render(request, 'medicamentos.html', context)


def agendamentos_view(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    data_url = request.GET.get('data')
    if data_url:
        try:
            hoje_referencia = datetime.strptime(data_url, '%Y-%m-%d').date()
        except ValueError:
            hoje_referencia = date.today()
    else:
        hoje_referencia = date.today()

    segunda_da_semana = hoje_referencia - timedelta(days=hoje_referencia.weekday())
    
    data_semana_anterior = segunda_da_semana - timedelta(days=7)
    data_semana_proxima = segunda_da_semana + timedelta(days=7)

    dias_semana = []
    nomes_curtos = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']
    hoje_real = date.today()
    
    for i in range(7):
        dia_iterado = segunda_da_semana + timedelta(days=i)
        dias_semana.append({
            'nome': nomes_curtos[i],
            'num': dia_iterado.day,
            'hoje': dia_iterado == hoje_real,
            'data_full': dia_iterado
        })

    fim_da_semana = segunda_da_semana + timedelta(days=6)
    vacinas = models.Vacina.objects.filter(pet__in=pets, data_aplicacao__range=[segunda_da_semana, fim_da_semana])
    consultas = models.Consulta.objects.filter(pet__in=pets, data_consulta__range=[segunda_da_semana, fim_da_semana])

    meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho',
             7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}

    context = {
        'tutor': tutor,
        'dias_semana': dias_semana,
        'vacinas': vacinas,
        'consultas': consultas,
        'mes_atual': meses[segunda_da_semana.month],
        'ano_atual': segunda_da_semana.year,
        'data_anterior': data_semana_anterior.strftime('%Y-%m-%d'),
        'data_proxima': data_semana_proxima.strftime('%Y-%m-%d'),
    }
    return render(request, 'agendamentos.html', context)
    # Removido o return duplicado


def diario_emocional_view(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    if request.method == "POST":
        pet_id = request.POST.get('pet_id')
        humor = request.POST.get('humor')
        relato = request.POST.get('relato')

        if not humor:
            messages.error(request, "Por favor, selecione um emoji de humor!")
        elif not relato:
            messages.error(request, "Escreva um pequeno relato sobre o pet.")
        else:
            try:
                models.DiarioEmocional.objects.create(
                    pet_id=pet_id,
                    humor=int(humor),
                    relato=relato
                )
                messages.success(request, "Comportamento registrado com sucesso!")
                return redirect('diario_emocional')
            except Exception as e:
                messages.error(request, "Erro técnico ao salvar no banco.")

    pet_selecionado = pets.first()
    recentes = models.DiarioEmocional.objects.filter(pet__in=pets).order_by('-data_registro')[:5]

    labels = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
    if pet_selecionado:
        registros = models.DiarioEmocional.objects.filter(pet=pet_selecionado).order_by('-data_registro')[:7]
        valores = [r.humor for r in reversed(registros)]
    else:
        valores = []

    while len(valores) < 7:
        valores.insert(0, 2)  # valor neutro

    return render(request, 'diario_emocional.html', {
        'pets': pets,
        'recentes': recentes,
        'pet_selecionado': pet_selecionado,
        'grafico_labels': json.dumps(labels),
        'grafico_valores': json.dumps(valores)
    })
