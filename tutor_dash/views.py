from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from django.db.models import Sum
from pet_app import models
# Certifique-se que get_tutor_logado e get_veterinario_logado existem em utils.py
from pet_app.utils import get_veterinario_logado, get_tutor_logado

# ========================================================
# ÁREA DO VETERINÁRIO
# ========================================================

def dash_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    try:
        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return redirect('login_veterinario')

    # Estatísticas
    total_pacientes = models.Pet.objects.count()
    
    consultas_hoje = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        data_consulta=date.today()
    ).count()

    # Busca flexível por "Crítico"
    casos_criticos = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        tipo_de_consulta__icontains='Crítico'
    ).count()

    # Soma o Faturamento (usando o novo campo valor_consulta)
    faturamento_dia = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        data_consulta=date.today()
    ).aggregate(total=Sum('valor_consulta'))['total'] or 0

    # Agenda de hoje (Ordenada por horário)
    agenda_hoje = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        data_consulta=date.today()
    ).select_related('id_pet', 'id_pet__id_tutor').order_by('horario_consulta')

    # Alertas (Ordenados por data recente)
    alertas = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        tipo_de_consulta__icontains='Alerta'
    ).select_related('id_pet').order_by('-data_consulta')

    context = {
        'veterinario': veterinario,
        'total_pacientes': total_pacientes,
        'consultas_hoje': consultas_hoje,
        'casos_criticos': casos_criticos,
        'faturamento_dia': faturamento_dia,
        'agenda_hoje': agenda_hoje,
        'alertas': alertas,
    }

    return render(request, 'dash_veterinario.html', context)


def perfil_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    try:
        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return redirect('login_veterinario')

    contatos = models.ContatoVeterinario.objects.filter(id_veterinario=veterinario)

    context = {
        'veterinario': veterinario,
        'contatos': contatos,
    }
    return render(request, 'veterinario_perfil.html', context)


def editar_perfil_veterinario(request):
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    try:
        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return redirect('login_veterinario')

    contatos = models.ContatoVeterinario.objects.filter(id_veterinario=veterinario)

    if request.method == "POST":
        # Atualiza dados básicos
        veterinario.nome = request.POST.get('nome')
        veterinario.email = request.POST.get('email')
        veterinario.crmv = request.POST.get('crmv')
        veterinario.uf_crmv = request.POST.get('uf_crmv')
        veterinario.telefone = request.POST.get('telefone')

        # Atualiza imagem
        if request.FILES.get('image_veterinario'):
            veterinario.imagem_perfil_veterinario = request.FILES['image_veterinario']

        veterinario.save()

        # Atualiza contatos (Remove e recria)
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

    context = {
        'veterinario': veterinario,
        'contatos': contatos,
    }
    return render(request, 'editar_perfil_veterinario.html', context)


# ========================================================
# ÁREA DO TUTOR
# ========================================================

def dash_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login') 

    try:
        # Busca o tutor
        tutor = models.Tutor.objects.get(id=tutor_data['id'])
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return redirect('login')

    context = {
        'tutor': tutor,
        'tutor_data': tutor_data
    }
    return render(request, 'dash_tutor.html', context)


def perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    try:
        tutor = models.Tutor.objects.get(id=tutor_data['id'])
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return redirect('login')

    context = {
        'tutor': tutor,
        'tutor_data': tutor_data
    }
    return render(request, 'tutor_perfil.html', context)


def editar_perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    contatos = models.ContatoTutor.objects.filter(id_tutor=tutor).order_by('-data_cadastro')

    if request.method == "POST":
        tutor.nome_tutor = request.POST.get('nome_tutor')
        tutor.cpf = request.POST.get('cpf')
        tutor.data_nascimento = request.POST.get('data_nascimento')
        tutor.endereco = request.POST.get('endereco')
        
        imagem_tutor = request.FILES.get('image_tutor')
        if imagem_tutor:
            tutor.imagem_perfil_tutor = imagem_tutor
            
        tutor.save()

        # Atualiza Contatos
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')

        models.ContatoTutor.objects.filter(id_tutor=tutor.id).delete()

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
        'contatos': contatos,
    }
    return render(request, 'editar_perfil.html', context)


# ------------------------
# Nova View: Meus Pets
# ------------------------
def meus_pets(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    try:
        tutor = models.Tutor.objects.get(id=tutor_data['id'])
        # Busca apenas os pets deste tutor
        pets = models.Pet.objects.filter(id_tutor=tutor)
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return redirect('login')

    context = {
        'tutor': tutor,
        'pets': pets,
    }
    return render(request, 'meus_pets.html', context)

# ------------------------
# Adicionar Pet
# ------------------------
# No topo do views.py, certifique-se que tem esses imports:
from django.shortcuts import render, redirect
from django.contrib import messages
from pet_app import models
from pet_app.utils import get_tutor_logado

def adicionar_pet(request):
    # 1. Verifica se está logado
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')
    
    # 2. Busca o objeto Tutor no banco
    try:
        tutor = models.Tutor.objects.get(id=tutor_data['id'])
    except models.Tutor.DoesNotExist:
        return redirect('login')

    # 3. Se o formulário foi enviado (POST)
    if request.method == "POST":
        # Pegamos os dados do HTML (request.POST) ao invés de JSON
        nome = request.POST.get('nome')
        especie = request.POST.get('especie')
        raca = request.POST.get('raca')
        data_nasc = request.POST.get('data_nascimento')
        sexo = request.POST.get('sexo')
        # Se os campos pelagem/castrado não existirem no form, usamos vazio ou padrão
        pelagem = request.POST.get('pelagem', 'Não informada') 
        castrado = request.POST.get('castrado', 'Não')

        # Criação do Prontuário (Obrigatório pelo seu Model)
        novo_prontuario = models.ProntuarioPet.objects.create(
            historico_veterinario=f"Prontuário inicial de {nome}",
            motivo_consulta="Cadastro no sistema",
            avaliacao_geral="Sem avaliações",
            procedimentos="-",
            diagnostico_conslusivo="-",
            observacao="-"
        )

        # Criação do Pet
        models.Pet.objects.create(
            nome=nome,
            especie=especie,
            raca=raca,
            data_nascimento=data_nasc,
            sexo=sexo,
            pelagem=pelagem,
            castrado=castrado,
            id_tutor=tutor,
            id_consulta=novo_prontuario
        )

        messages.success(request, f"Pet {nome} cadastrado com sucesso!")
        return redirect('meus_pets') # Volta para a lista de pets

    # 4. Se for apenas abrir a página (GET), mostra o formulário
    # Precisamos criar esse HTML abaixo
    context = {
        'tutor': tutor
    }
    return render(request, 'adicionar_pet.html', context)

# ------------------------
# Excluir Pet
# ------------------------
def excluir_pet(request, pet_id):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    # Busca o pet e garante que ele pertence ao tutor logado (Segurança)
    pet = models.Pet.objects.filter(id=pet_id, id_tutor_id=tutor_data['id']).first()
    
    if pet:
        nome_pet = pet.nome
        pet.delete()
        messages.success(request, f"{nome_pet} foi removido.")
    else:
        messages.error(request, "Pet não encontrado ou permissão negada.")

    return redirect('meus_pets')