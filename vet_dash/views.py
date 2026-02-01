from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime, timedelta, date
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import json
from pet_app import models
from pet_app.utils import get_veterinario_logado
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError


# ------------------------
# Dashboard do Veterinário
# ------------------------
def dash_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')

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
        return redirect('login')

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
        return redirect('login')

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

def aceitar_consulta(request, consulta_id):
    vet_login = get_veterinario_logado(request)
    if not get_veterinario_logado(request):
        return redirect('login')  # ajuste o nome da sua view de login vet

    consulta = get_object_or_404(models.Consulta, id=consulta_id)
    
    if consulta.veterinario.id != vet_login['id']:
        messages.error(request, "Esta consulta não pertence à sua conta.")
        return redirect('agenda_vet')

    if consulta.status != 'Pendente':
        messages.warning(request, f"Status atual: {consulta.status}. Não é possível aceitar.")
        return redirect('agenda_vet')

    consulta.status = 'Confirmado'
    consulta.save()
    messages.success(request, f"Consulta de {consulta.pet.nome} confirmada!")
    
    return redirect('agenda_vet')  # ou com ?data=... para manter o filtro

def rejeitar_consulta(request, consulta_id):
    vet_login = get_veterinario_logado(request)
    if not get_veterinario_logado(request):
        return redirect('login')

    consulta = get_object_or_404(models.Consulta, id=consulta_id)
    
    if consulta.veterinario.id != vet_login['id']:
        messages.error(request, "Esta consulta não pertence à sua conta.")
        return redirect('agenda_vet')

    if consulta.status != 'Pendente':
        messages.warning(request, f"Status atual: {consulta.status}. Não é possível rejeitar.")
        return redirect('agenda_vet')

    consulta.status = 'Cancelado'
    consulta.save()
    messages.success(request, f"Consulta de {consulta.pet.nome} rejeitada.")
    
    return redirect('agenda_vet')

# ------------------------
# Prontuários
# ------------------------
def prontuarios_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    pet_id = request.GET.get('pet_id')
    pet_selecionado = None
    ultimos_prontuarios = []

    if pet_id:
        pet_selecionado = models.Pet.objects.filter(id=pet_id).first()
        ultimos_prontuarios = models.Prontuariopet.objects.filter(pet_id=pet_id).order_by('-id')[:5]

    if request.method == "POST" and pet_id:
        pet = models.Pet.objects.filter(id=pet_id).first()
        observacoes = request.POST.get('anotacoes', '')
        
        if pet:
            models.Prontuariopet.objects.create(
                pet=pet,
                veterinario=veterinario,
                observacao=observacoes or "Sem observações adicionais",
                avaliacao_geral="Registrado pelo veterinário via dashboard",
            )
            messages.success(request, "Prontuário salvo com sucesso!")
        else:
            messages.error(request, "Pet não encontrado.")
        
        return redirect(f'/vet_dash/prontuarios/?pet_id={pet_id}')

    pacientes = models.Pet.objects.all().order_by('nome')

    context = {
        'veterinario': veterinario,
        'pacientes': pacientes,
        'pet_selecionado': pet_selecionado,
        'ultimos_prontuarios': ultimos_prontuarios,
    }
    return render(request, 'prontuarios.html', context)


# ------------------------
# Financeiro
# ------------------------
def financeiro_view(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')

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
        return redirect('login')
    
    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    contatos = models.ContatoVeterinario.objects.filter(veterinario_id=veterinario.id)

    try:
        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    except models.Veterinario.DoesNotExist:
        messages.error(request, "Veterinário não encontrado.")
        return redirect('login')
    
    if request.method == "POST":
        # Coletar dados do POST
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        crmv = request.POST.get('crmv', '').strip()
        uf_crmv = request.POST.get('uf_crmv', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        image_veterinario = request.FILES.get('image_veterinario')
        
        # Coletar contatos do POST (listas)
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')
        
        # Validações básicas
        errors = []
        if not nome:
            errors.append("Nome é obrigatório.")
        if not email or '@' not in email:
            errors.append("Email inválido.")
        if not crmv:
            errors.append("CRMV é obrigatório.")
        if not uf_crmv:
            errors.append("UF do CRMV é obrigatória.")
        if telefone and not telefone.isdigit():
            errors.append("Telefone deve conter apenas números.")
        
        # Validação de imagem
        if image_veterinario:
            if not isinstance(image_veterinario, UploadedFile):
                errors.append("Imagem inválida.")
            elif image_veterinario.content_type not in ['image/jpeg', 'image/png']:
                errors.append("Apenas imagens JPEG ou PNG são permitidas.")
            elif image_veterinario.size > 5 * 1024 * 1024:  # 5MB
                errors.append("A imagem deve ter no máximo 5MB.")
        
        # Validação de contatos
        contatos_validos = []
        for i in range(len(tipos)):
            tipo = tipos[i].strip()
            ddd = ddds[i].strip()
            numero = numeros[i].strip()
            if ddd or numero:  # Só validar se pelo menos um campo preenchido
                if not ddd.isdigit() or len(ddd) != 2:
                    errors.append(f"DDD inválido para contato {i+1}.")
                if not numero.isdigit() or len(numero) < 8:
                    errors.append(f"Número inválido para contato {i+1}.")
                contatos_validos.append({'tipo_contato': tipo, 'ddd': ddd, 'numero': numero})
        
        if errors:
            for error in errors:
                messages.error(request, error)
            # Recarregar contatos existentes para o template
            contatos = models.ContatoVeterinario.objects.filter(veterinario=veterinario)
            return redirect('perfil_veterinario')
        
        # Tentativa de salvar com transação
        try:
            with transaction.atomic():
                # Atualizar Veterinario
                veterinario.nome = nome
                veterinario.email = email
                veterinario.crmv = crmv
                veterinario.uf_crmv = uf_crmv
                veterinario.telefone = telefone
                if image_veterinario:
                    veterinario.imagem_perfil_veterinario = image_veterinario
                veterinario.save()
                
                # Manipulação eficiente de contatos: comparar com existentes
                contatos_existentes = list(models.ContatoVeterinario.objects.filter(veterinario=veterinario))
                ids_existentes = {c.id for c in contatos_existentes}
                
                # Criar ou atualizar contatos
                for contato_data in contatos_validos:
                    # Verificar se já existe (simplificado: assumir que tipo+ddd+numero é único por vet)
                    existing = next((c for c in contatos_existentes if c.tipo_contato == contato_data['tipo_contato'] and c.ddd == contato_data['ddd'] and c.numero == contato_data['numero']), None)
                    if existing:
                        # Atualizar se necessário (aqui, assumindo que dados são os mesmos, mas pode expandir)
                        pass
                    else:
                        models.ContatoVeterinario.objects.create(
                            veterinario=veterinario,
                            **contato_data
                        )
                
                # Deletar contatos não enviados (aqueles que não estão em contatos_validos)
                for c in contatos_existentes:
                    if not any(c.tipo_contato == cd['tipo_contato'] and c.ddd == cd['ddd'] and c.numero == cd['numero'] for cd in contatos_validos):
                        c.delete()
            
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('perfil_veterinario')
        
        except IntegrityError as e:
            messages.error(request, f"Erro ao salvar: {str(e)}. Verifique se o email ou CRMV já estão em uso.")
        except ValidationError as e:
            messages.error(request, f"Dados inválidos: {str(e)}")
        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}. Tente novamente.")
    
    
    return render(request, 'vet_perfil.html', {
        'veterinario': veterinario, 
        'contatos': contatos
    })

def editar_perfil_veterinario(request):
    # Verificar se o veterinário está logado
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')
    
    try:
        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    except models.Veterinario.DoesNotExist:
        messages.error(request, "Veterinário não encontrado.")
        return redirect('login')
    
    if request.method == "POST":
        # Coletar dados do POST
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        crmv = request.POST.get('crmv', '').strip()
        uf_crmv = request.POST.get('uf_crmv', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        image_veterinario = request.FILES.get('image_veterinario')
        
        # Coletar contatos do POST (listas)
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')
        
        # Validações básicas
        errors = []
        if not nome:
            errors.append("Nome é obrigatório.")
        if not email or '@' not in email:
            errors.append("Email inválido.")
        if not crmv:
            errors.append("CRMV é obrigatório.")
        if not uf_crmv:
            errors.append("UF do CRMV é obrigatória.")
        if telefone and not telefone.isdigit():
            errors.append("Telefone deve conter apenas números.")
        
        # Validação de imagem
        if image_veterinario:
            if not isinstance(image_veterinario, UploadedFile):
                errors.append("Imagem inválida.")
            elif image_veterinario.content_type not in ['image/jpeg', 'image/png']:
                errors.append("Apenas imagens JPEG ou PNG são permitidas.")
            elif image_veterinario.size > 5 * 1024 * 1024:  # 5MB
                errors.append("A imagem deve ter no máximo 5MB.")
        
        # Validação de contatos
        contatos_validos = []
        for i in range(len(tipos)):
            tipo = tipos[i].strip()
            ddd = ddds[i].strip()
            numero = numeros[i].strip()
            if ddd or numero:  # Só validar se pelo menos um campo preenchido
                if not ddd.isdigit() or len(ddd) != 2:
                    errors.append(f"DDD inválido para contato {i+1}.")
                if not numero.isdigit() or len(numero) < 8:
                    errors.append(f"Número inválido para contato {i+1}.")
                contatos_validos.append({'tipo_contato': tipo, 'ddd': ddd, 'numero': numero})
        
        if errors:
            for error in errors:
                messages.error(request, error)
            # Recarregar contatos existentes para o template
            contatos = models.ContatoVeterinario.objects.filter(veterinario=veterinario)
            return render(request, 'editar_perfil_veterinario.html', {
                'veterinario': veterinario,
                'contatos': contatos
            })
        
        # Tentativa de salvar com transação
        try:
            with transaction.atomic():
                # Atualizar Veterinario
                veterinario.nome = nome
                veterinario.email = email
                veterinario.crmv = crmv
                veterinario.uf_crmv = uf_crmv
                veterinario.telefone = telefone
                if image_veterinario:
                    veterinario.imagem_perfil_veterinario = image_veterinario
                veterinario.save()
                
                # Manipulação eficiente de contatos: comparar com existentes
                contatos_existentes = list(models.ContatoVeterinario.objects.filter(veterinario=veterinario))
                ids_existentes = {c.id for c in contatos_existentes}
                
                # Criar ou atualizar contatos
                for contato_data in contatos_validos:
                    # Verificar se já existe (simplificado: assumir que tipo+ddd+numero é único por vet)
                    existing = next((c for c in contatos_existentes if c.tipo_contato == contato_data['tipo_contato'] and c.ddd == contato_data['ddd'] and c.numero == contato_data['numero']), None)
                    if existing:
                        # Atualizar se necessário (aqui, assumindo que dados são os mesmos, mas pode expandir)
                        pass
                    else:
                        models.ContatoVeterinario.objects.create(
                            veterinario=veterinario,
                            **contato_data
                        )
                
                # Deletar contatos não enviados (aqueles que não estão em contatos_validos)
                for c in contatos_existentes:
                    if not any(c.tipo_contato == cd['tipo_contato'] and c.ddd == cd['ddd'] and c.numero == cd['numero'] for cd in contatos_validos):
                        c.delete()
            
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('perfil_veterinario')
        
        except IntegrityError as e:
            messages.error(request, f"Erro ao salvar: {str(e)}. Verifique se o email ou CRMV já estão em uso.")
        except ValidationError as e:
            messages.error(request, f"Dados inválidos: {str(e)}")
        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}. Tente novamente.")
    
    # GET: Carregar dados existentes
    contatos = models.ContatoVeterinario.objects.filter(veterinario=veterinario)
    return render(request, 'editar_perfil.html', {
        'veterinario': veterinario,
        'contatos': contatos
    })


# ------------------------
# Detalhes do Pet (para o Veterinário)
# ------------------------
def detalhe_pet_view(request, pet_id):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')

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


# ========================================================
# MENSAGENS
# ========================================================

def mensagens_vet(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    
    # Pega todos os tutores para exibir na lista de contatos
    contatos = models.Tutor.objects.all().order_by('nome_tutor')
    
    # Pega o tutor selecionado se houver
    tutor_selecionado = None
    mensagens = []
    
    tutor_id = request.GET.get('tutor_id')
    if tutor_id:
        try:
            tutor_selecionado = models.Tutor.objects.get(id=tutor_id)
            mensagens = models.Mensagem.objects.filter(
                VETERINARIO=veterinario,
                TUTOR=tutor_selecionado
            ).order_by('DATA_ENVIO')
        except models.Tutor.DoesNotExist:
            pass

    context = {
        'veterinario': veterinario,
        'contatos': contatos,
        'tutor_selecionado': tutor_selecionado,
        'mensagens': mensagens,
    }
    return render(request, 'mensagensvet.html', context)


def enviar_mensagem_vet(request):
    if request.method == "POST":
        vet_data = get_veterinario_logado(request)
        if not vet_data:
            return redirect('login')

        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
        tutor_id = request.POST.get('tutor_id')
        conteudo = request.POST.get('mensagem')

        try:
            tutor = models.Tutor.objects.get(id=tutor_id)
            models.Mensagem.objects.create(
                VETERINARIO=veterinario,
                TUTOR=tutor,
                CONTEUDO=conteudo,
                ENVIADO_POR='VETERINARIO'
            )
        except models.Tutor.DoesNotExist:
            pass

        return redirect(f'/vet_dash/mensagens/?tutor_id={tutor_id}')

    return redirect('mensagens_vet')

def perfil_pet_vet(request, pet_id):
    """Exibe e permite editar perfil do pet para o veterinário"""
    pet = get_object_or_404(models.Pet, id=pet_id)
    
    if request.method == "POST":
        # Se veio nome_vacina, salva vacina
        if request.POST.get('nome_vacina'):
            models.Vacina.objects.create(
                nome=request.POST.get('nome_vacina'),
                data_aplicacao=request.POST.get('data_aplicacao'),
                proxima_dose=request.POST.get('proxima_dose') or None,
                pet=pet
            )
        else:
            # Salva os dados do Pet
            pet.nome = request.POST.get('nome') or pet.nome
            pet.peso = request.POST.get('peso') or pet.peso
            pet.sexo = request.POST.get('sexo') or pet.sexo
            pet.descricao = request.POST.get('descricao') or pet.descricao
            pet.especie = request.POST.get('especie') or pet.especie
            pet.raca = request.POST.get('raca') or pet.raca
            pet.pelagem = request.POST.get('pelagem') or pet.pelagem
            pet.personalidade = request.POST.get('personalidade') or pet.personalidade

            if request.FILES.get('imagem'):
                pet.imagem = request.FILES.get('imagem')
            
            pet.save()
        
        return redirect('perfil_pet_vet', pet_id=pet.id)

    # GET: Busca as vacinas atualizadas
    vacinas = models.Vacina.objects.filter(pet_id=pet.id).order_by('-data_aplicacao')
    proxima_consulta = models.Consulta.objects.filter(
        pet_id=pet.id, 
        data_consulta__gte=timezone.now().date()
    ).order_by('data_consulta').first()

    list_personalidades = []
    if pet.personalidade:
        list_personalidades = [p.strip() for p in pet.personalidade.split(',') if p.strip()]

    context = {
        'pet': pet,
        'vacinas': vacinas,
        'proxima_consulta': proxima_consulta,
        'list_personalidades': list_personalidades,
    }
    return render(request, 'detalhes_pet.html', context)


# ========================================================
# EXCLUSÃO DE AGENDAMENTOS (CONSULTAS E VACINAS)
# ========================================================

def excluir_consulta_vet(request, consulta_id):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    consulta = models.Consulta.objects.filter(
        id=consulta_id,
        pet__veterinario=veterinario
    ).first()

    if consulta:
        consulta.delete()
        messages.success(request, "Consulta removida com sucesso!")
    else:
        messages.error(request, "Consulta não encontrada.")

    return redirect('agenda_vet')


def excluir_vacina_vet(request, vacina_id):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    vacina = models.Vacina.objects.filter(
        id=vacina_id,
        pet__veterinario=veterinario
    ).first()

    if vacina:
        vacina.delete()
        messages.success(request, "Registro de vacinação removido com sucesso!")
    else:
        messages.error(request, "Registro não encontrado.")

    return redirect('agenda_vet')
