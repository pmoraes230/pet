from django.contrib import messages
from django.shortcuts import redirect, render
from pet_app import models
from pet_app.utils import get_veterinario_logado

# Dashboard do veterinário
def dash_veterinario(request):
    vet_data = get_veterinario_logado(request)

    if not vet_data:
        return redirect('login_veterinario')  # ou sua página de login

    try:
        veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return redirect('login_veterinario')

    context = {
        'veterinario': veterinario,
        'vet_data': vet_data
    }
    return render(request, 'dash_veterinario.html', context)


# Perfil do veterinário
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
        'contatos': contatos
    }
    return render(request, 'veterinario_perfil.html', context)


# Editar perfil do veterinário
def editar_perfil_veterinario(request):
    vet_data = get_veterinario_logado(request)

    if not vet_data:
        return redirect('login_veterinario')

    veterinario = models.Veterinario.objects.get(id=vet_data['id'])
    contatos = models.ContatoVeterinario.objects.filter(id_veterinario=veterinario)

    if request.method == "POST":
        # Atualiza dados do veterinário
        veterinario.nome = request.POST.get('nome')
        veterinario.email = request.POST.get('email')
        veterinario.crmv = request.POST.get('crmv')
        veterinario.uf_crmv = request.POST.get('uf_crmv')
        veterinario.telefone = request.POST.get('telefone')
        veterinario.save()

        # Processa contatos
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')

        # Deleta todos e recria (simples e seguro)
        models.ContatoVeterinario.objects.filter(id_veterinario=veterinario.id).delete()

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
        'contatos': contatos
    }
    return render(request, 'editar_perfil_veterinario.html', context)
