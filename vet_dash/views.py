from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime, timedelta, date
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import json
from pet_app import models
from pet_app.utils import get_veterinario_logado


# ------------------------
# Dashboard do Veterinário
# ------------------------
def dash_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    total_pacientes = models.Pet.objects.count()

    consultas_hoje = models.Consulta.objects.filter(
        veterinario=veterinario,
        data_consulta=date.today()
    ).count()

    casos_criticos = models.Consulta.objects.filter(
        veterinario=veterinario,
        tipo_de_consulta__icontains='Crítico'
    ).count()

    faturamento_dia = models.Consulta.objects.filter(
        veterinario=veterinario,
        data_consulta=date.today()
    ).aggregate(total=Sum('valor_consulta'))['total'] or 0

    agenda_hoje = models.Consulta.objects.filter(
        veterinario=veterinario,
        data_consulta=date.today()
    ).select_related('pet', 'pet__tutor').order_by('horario_consulta')

    alertas = models.Consulta.objects.filter(
        veterinario=veterinario,
        tipo_de_consulta__icontains='Alerta'
    ).select_related('pet').order_by('-data_consulta')

    context = {
        'veterinario': veterinario,
        'total_pacientes': total_pacientes,
        'consultas_hoje': consultas_hoje,
        'casos_criticos': casos_criticos,
        'faturamento_dia': faturamento_dia,
        'agenda_hoje': agenda_hoje,
        'alertas': alertas,
    }
    return render(request, 'vet_dash.html', context)


# ------------------------
# Lista de Pacientes
# ------------------------
def pacientes_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    pacientes = models.Pet.objects.all().order_by('nome')

    context = {
        'veterinario': veterinario,
        'pacientes': pacientes,
    }
    return render(request, 'pacientes.html', context)


# ------------------------
# Agenda Completa
# ------------------------
def agenda_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    if request.method == "POST":
        pet_id = request.POST.get('pet')
        data_sel = request.POST.get('data')
        hora_sel = request.POST.get('hora')
        tipo_sel = request.POST.get('tipo')
        obs_sel = request.POST.get('obs')

        try:
            pet_obj = models.Pet.objects.get(id=pet_id)
            models.Consulta.objects.create(
                veterinario=veterinario,
                pet=pet_obj,
                data_consulta=data_sel,
                horario_consulta=hora_sel,
                tipo_de_consulta=tipo_sel,
                observacoes=obs_sel,
                status='Agendado'
            )
            messages.success(request, f"Consulta para {pet_obj.nome} agendada com sucesso!")
        except Exception:
            messages.error(request, "Erro ao agendar consulta. Verifique os dados.")

        return redirect(f'/vet_dash/agenda/?data={data_sel}')

        return redirect(f'/vet_dash/agenda/?data={data_sel}')

    # Lógica do calendário
    str_data = request.GET.get('data')
    if str_data:
        data_foco = datetime.strptime(str_data, '%Y-%m-%d').date()
    else:
        data_foco = date.today()

    start_of_week = data_foco - timedelta(days=data_foco.weekday())

    dias_semana = []
    nomes_dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB', 'DOM']

    for i in range(7):
        dia_aux = start_of_week + timedelta(days=i)
        dias_semana.append({
            'nome': nomes_dias[i],
            'num': dia_aux.day,
            'data_completa': dia_aux.strftime('%Y-%m-%d'),
            'hoje': dia_aux == date.today(),
            'selecionado': dia_aux == data_foco
        })

    meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_atual = meses[data_foco.month]
    ano_atual = data_foco.year

    data_anterior = (data_foco - timedelta(days=7)).strftime('%Y-%m-%d')
    data_proxima = (data_foco + timedelta(days=7)).strftime('%Y-%m-%d')

    agenda_completa = models.Consulta.objects.filter(
        veterinario=veterinario,
        data_consulta=data_foco
    ).select_related(
        'pet', 'pet__tutor'
    ).order_by('horario_consulta')

    pacientes = models.Pet.objects.all().order_by('nome')

    context = {
        'veterinario': veterinario,
        'agenda': agenda_completa,
        'pacientes': pacientes,
        'dias_semana': dias_semana,
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'data_anterior': data_anterior,
        'data_proxima': data_proxima,
        'data_foco': data_foco,
    }

    return render(request, 'agenda.html', context)



# ------------------------
# Prontuários
# ------------------------
def prontuarios_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    pet_id = request.GET.get('pet_id')
    pet_selecionado = None

    if pet_id:
        pet_selecionado = models.Pet.objects.filter(id=pet_id).first()

    if request.method == "POST" and pet_id:
        observacoes = request.POST.get('anotacoes', '')
        models.Prontuariopet.objects.create(
            observacao=observacoes or "Sem observações adicionais",
            avaliacao_geral="Registrado pelo veterinário via dashboard",
        )
        messages.success(request, "Prontuário salvo com sucesso!")
        return redirect(f'/vet_dash/prontuarios/?pet_id={pet_id}')

    pacientes = models.Pet.objects.all().order_by('nome')

    context = {
        'veterinario': veterinario,
        'pacientes': pacientes,
        'pet_selecionado': pet_selecionado,
    }
    return render(request, 'prontuarios.html', context)


# ------------------------
# Financeiro
# ------------------------
def financeiro_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    hoje = date.today()

    consultas_mes = models.Consulta.objects.filter(
        veterinario=veterinario,
        data_consulta__month=hoje.month,
        data_consulta__year=hoje.year
    )

    entradas_mes = consultas_mes.aggregate(
        total=Sum('valor_consulta')
    )['total'] or 0

    saidas_mock = float(entradas_mes) * 0.3
    saldo_liquido = float(entradas_mes) - saidas_mock

    transacoes = models.Consulta.objects.filter(
        veterinario=veterinario
    ).exclude(
        valor_consulta=0
    ).select_related(
        'pet'
    ).order_by(
        '-data_consulta', '-horario_consulta'
    )[:5]

    dados_grafico = models.Consulta.objects.filter(
        veterinario=veterinario
    ).annotate(
        mes=ExtractMonth('data_consulta')
    ).values(
        'mes'
    ).annotate(
        total=Sum('valor_consulta')
    ).order_by('mes')

    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai",
                   "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    labels = []
    valores = []

    for item in dados_grafico:
        if item['mes']:
            labels.append(meses_nomes[item['mes'] - 1])
            valores.append(float(item['total']))

    if not labels:
        labels, valores = ["Sem dados"], [0]

    context = {
        'veterinario': veterinario,
        'entradas_mes': entradas_mes,
        'saidas_mes': saidas_mock,
        'saldo_liquido': saldo_liquido,
        'transacoes': transacoes,
        'labels_json': json.dumps(labels),
        'valores_json': json.dumps(valores),
    }

    return render(request, 'financeiro.html', context)


# ------------------------
# Perfil do Veterinário
# ------------------------
def perfil_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')
    
    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    contatos = models.ContatoVeterinario.objects.filter(id_veterinario=veterinario)
    
    # MUDE AQUI: Verifique qual é o nome do seu arquivo HTML
    # Se você criou como vet_perfil.html, mude para:
    return render(request, 'vet_perfil.html', {
        'veterinario': veterinario, 
        'contatos': contatos
    })


def editar_perfil_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    if request.method == "POST":
        veterinario.nome = request.POST.get('nome')
        veterinario.email = request.POST.get('email')
        veterinario.crmv = request.POST.get('crmv')
        veterinario.uf_crmv = request.POST.get('uf_crmv')
        veterinario.telefone = request.POST.get('telefone')

        if request.FILES.get('image_veterinario'):
            veterinario.imagem_perfil_veterinario = request.FILES['image_veterinario']

        veterinario.save()

        # Atualiza contatos
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')

        models.ContatoVeterinario.objects.filter(
            veterinario=veterinario).delete()  # Correção aqui também

        for i in range(len(tipos)):
            if ddds[i].strip() and numeros[i].strip():
                models.ContatoVeterinario.objects.create(
                    veterinario=veterinario,
                    tipo_contato=tipos[i],
                    ddd=ddds[i],
                    numero=numeros[i]
                )

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('perfil_veterinario')

    contatos = models.ContatoVeterinario.objects.filter(veterinario=veterinario)
    return render(request, 'editar_perfil_veterinario.html', {
        'veterinario': veterinario,
        'contatos': contatos
    })


# ------------------------
# Detalhes do Pet (para o Veterinário)
# ------------------------
def detalhe_pet_view(request, pet_id):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    pet = get_object_or_404(models.Pet, id=pet_id)

    if request.method == "POST":
        pet.peso = request.POST.get('peso')
        pet.sexo = request.POST.get('sexo')
        pet.descricao = request.POST.get('descricao')
        pet.especie = request.POST.get('especie')
        pet.raca = request.POST.get('raca')
        pet.pelagem = request.POST.get('pelagem')
        pet.personalidade = request.POST.get('personalidade')

        if request.FILES.get('imagem'):
            pet.imagem = request.FILES['imagem']

        pet.save()
        messages.success(
            request, f"Dados de {pet.nome} atualizados com sucesso!")
        return redirect('detalhes_pet', pet_id=pet.id)

    proxima_consulta = models.Consulta.objects.filter(
        pet=pet,
        data_consulta__gte=date.today()
    ).order_by('data_consulta').first()

    vacinas = models.Vacina.objects.filter(pet=pet).order_by('-data_aplicacao')

    list_personalidades = pet.personalidade.split(
        ',') if pet.personalidade else []

    context = {
        'veterinario': veterinario,
        'pet': pet,
        'proxima_consulta': proxima_consulta,
        'vacinas': vacinas,
        'list_personalidades': list_personalidades,
    }
    return render(request, 'detalhes_pet.html', context)