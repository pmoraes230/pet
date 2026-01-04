from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta, date
from django.db.models import Sum
from pet_app import models
from pet_app.utils import get_veterinario_logado
import calendar
import json
from django.db.models.functions import ExtractMonth  # <--- ESSA LINHA FALTAVA



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
# LISTA DE PACIENTES
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
# AGENDA COMPLETA (COM POP-UP DE AGENDAMENTO)
# ------------------------
def agenda_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data: 
        return redirect('login_veterinario')
    
    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    # --- SALVAR NOVO AGENDAMENTO (POST do Modal) ---
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
                status='Agendado' # Status padrão inicial
            )
            messages.success(request, f"Consulta para {pet_obj.nome} agendada com sucesso!")
        except Exception as e:
            messages.error(request, "Erro ao agendar consulta. Verifique os dados.")
        
        return redirect(f'/vet_dash/agenda/?data={data_sel}') # Redireciona para o dia do agendamento

    # --- LÓGICA DO CALENDÁRIO STRIP (GET) ---
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

    meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_atual = meses[data_foco.month]
    ano_atual = data_foco.year
    
    data_anterior = (data_foco - timedelta(days=7)).strftime('%Y-%m-%d')
    data_proxima = (data_foco + timedelta(days=7)).strftime('%Y-%m-%d')

    # Busca consultas do dia e lista de pacientes para o Modal
    agenda_completa = models.Consulta.objects.filter(
        veterinario=veterinario,
        data_consulta=data_foco
    ).select_related('pet', 'pet__tutor').order_by('horario_consulta')

    pacientes = models.Pet.objects.all().order_by('nome')

    context = {
        'veterinario': veterinario,
        'agenda': agenda_completa,
        'pacientes': pacientes, # ESSENCIAL para o Select do Modal
        'dias_semana': dias_semana,
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'data_anterior': data_anterior,
        'data_proxima': data_proxima,
        'data_foco': data_foco,
    }
    return render(request, 'agenda.html', context)


# ------------------------
# PRONTUÁRIOS
# ------------------------
def prontuarios_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data: 
        return redirect('login_veterinario')
    
    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    pacientes = models.Pet.objects.all().order_by('nome')

    context = {
        'veterinario': veterinario,
        'pacientes': pacientes,
    }
    return render(request, 'prontuarios.html', context)


# ------------------------
# FINANCEIRO
# ------------------------
# ------------------------
# FINANCEIRO
# ------------------------
def financeiro_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data: 
        return redirect('login_veterinario')
    
    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    # 1. Resumo do Mês Atual
    hoje = date.today()
    consultas_mes = models.Consulta.objects.filter(
        veterinario=veterinario, # Ajustado para o nome que o Django mapeou
        data_consulta__month=hoje.month,
        data_consulta__year=hoje.year
    )
    
    entradas_mes = consultas_mes.aggregate(total=Sum('valor_consulta'))['total'] or 0
    saidas_mock = float(entradas_mes) * 0.3 
    saldo_liquido = float(entradas_mes) - saidas_mock

    # 2. Transações Recentes
    transacoes = models.Consulta.objects.filter(
        veterinario=veterinario
    ).exclude(valor_consulta=0).select_related('pet').order_by('-data_consulta', '-horario_consulta')[:5]

    # 3. Dados para o Gráfico (Usando o ExtractMonth importado)
    dados_grafico = models.Consulta.objects.filter(veterinario=veterinario)\
        .annotate(mes=ExtractMonth('data_consulta'))\
        .values('mes')\
        .annotate(total=Sum('valor_consulta'))\
        .order_by('mes')

    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    labels = []
    valores = []
    
    for item in dados_grafico:
        if item['mes']: # Garante que o mês não seja nulo
            labels.append(meses_nomes[item['mes']-1])
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
# PERFIL E EDIÇÃO
# ------------------------
def perfil_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data: 
        return redirect('login_veterinario')
    
    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    contatos = models.ContatoVeterinario.objects.filter(id_veterinario=veterinario)
    
    return render(request, 'veterinario_perfil.html', {
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
        
        models.ContatoVeterinario.objects.filter(id_veterinario=veterinario).delete()
        
        for i in range(len(tipos)):
            if ddds[i].strip() and numeros[i].strip():
                models.ContatoVeterinario.objects.create(
                    id_veterinario=veterinario, 
                    tipo_contato=tipos[i], 
                    ddd=ddds[i], 
                    numero=numeros[i]
                )

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('perfil_veterinario')

    contatos = models.ContatoVeterinario.objects.filter(id_veterinario=veterinario)
    return render(request, 'editar_perfil_veterinario.html', {
        'veterinario': veterinario, 
        'contatos': contatos
    })

def prontuarios_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data: return redirect('login_veterinario')
    veterinario = models.Veterinario.objects.get(id=vet_data['id'])

    # 1. Pega o ID do pet da URL (ex: ?pet_id=5)
    pet_id = request.GET.get('pet_id')
    pet_selecionado = None
    if pet_id:
        pet_selecionado = models.Pet.objects.filter(id=pet_id).first()

    # 2. Lógica para SALVAR o prontuário
    if request.method == "POST":
        observacoes = request.POST.get('anotacoes')
        # Aqui você pode salvar na tabela prontuariopet
        # No seu banco a tabela prontuariopet não tem FK direta com Pet, 
        # mas geralmente salvamos vinculado a uma consulta ou histórico.
        models.Prontuariopet.objects.create(
            observacao=observacoes,
            avaliacao_geral="Consulta via Dashboard",
            # Adicione outros campos se necessário
        )
        messages.success(request, "Prontuário salvo com sucesso!")
        return redirect(f'/vet_dash/prontuarios/?pet_id={pet_id}')

    # 3. Lista de pacientes para o seletor
    pacientes = models.Pet.objects.all().order_by('nome')

    context = {
        'veterinario': veterinario,
        'pacientes': pacientes,
        'pet_selecionado': pet_selecionado,
    }
    return render(request, 'prontuarios.html', context)