from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from pet_app import models
from pet_app.utils import get_tutor_logado

# Create your views here.
def dash_tutor(request):
    tutor_data = get_tutor_logado(request)
    
    if not tutor_data:
        return redirect('login')  # ou sua página de login

    try:
        tutor = models.Tutor.objects.prefetch_related('pet_set').get(id=tutor_data['id'])
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return redirect('login')

    context = {
        'tutor': tutor,
        'tutor_data': tutor_data

    }
    return render(request, 'dash_tutor/dash_tutor.html', context)

def perfil_tutor(request):
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

    return render(request, 'edit_tutor/tutor_perfil.html', context)

def editar_perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    contatos = models.ContatoTutor.objects.filter(id_tutor=tutor).order_by('-data_cadastro')

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

    try:
        tutor = models.Tutor.objects.get(id=tutor_data['id'])
    except models.Tutor.DoesNotExist:
        messages.error(request, "Erro ao encontrar sua conta.")
        return redirect('login')

    tutor.status_conta = False
    tutor.save()

    logout(request)
    request.session.flush() 

    messages.success(request, "Sua conta foi desativada com sucesso. "
                              "Você pode reativá-la entrando em contato com o suporte.")
    
    return redirect('login')