from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from django.db.models import Sum
from pet_app import models
from pet_app.utils import get_veterinario_logado

# ------------------------
# Dashboard do Veterinário
# ------------------------
def dash_veterinario(request):
    # 1. Verificação de Login
    vet_data = get_veterinario_logado(request)
    if not vet_data:
        return redirect('login_veterinario')

    try:
        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return redirect('login_veterinario')

    # 2. Estatísticas
    total_pacientes = models.Pet.objects.count()
    
    consultas_hoje = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        data_consulta=date.today()
    ).count()

    # Uso 'icontains' para pegar "Crítico", "critico", etc.
    casos_criticos = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        tipo_de_consulta__icontains='Crítico'
    ).count()

    # Soma o valor_consulta. O "or 0" garante que não quebre se for None
    faturamento_dia = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        data_consulta=date.today()
    ).aggregate(total=Sum('valor_consulta'))['total'] or 0

    # 3. Agenda de hoje
    # Adicionado .order_by('horario_consulta') para ordenar corretamente
    agenda_hoje = models.Consulta.objects.filter(
        id_veterinario=veterinario,
        data_consulta=date.today()
    ).select_related('id_pet', 'id_pet__id_tutor').order_by('horario_consulta')

    # 4. Alertas
    # Adicionado .order_by('-data_consulta') para mostrar os mais recentes primeiro
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

    return render(request, 'vet_dash.html', context)


# ------------------------
# Perfil do Veterinário
# ------------------------
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


# ------------------------
# Editar Perfil do Veterinário
# ------------------------
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
        # ------------------------
        # Atualiza dados do veterinário
        # ------------------------
        veterinario.nome = request.POST.get('nome')
        veterinario.email = request.POST.get('email')
        veterinario.crmv = request.POST.get('crmv')
        veterinario.uf_crmv = request.POST.get('uf_crmv')
        veterinario.telefone = request.POST.get('telefone')

        # Atualiza a imagem de perfil, se enviada
        if request.FILES.get('image_veterinario'):
            veterinario.imagem_perfil_veterinario = request.FILES['image_veterinario']

        veterinario.save()

        # ------------------------
        # Atualiza contatos
        # ------------------------
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')

        # Remove contatos antigos para recriar
        models.ContatoVeterinario.objects.filter(id_veterinario=veterinario).delete()

        # Cria os novos contatos
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