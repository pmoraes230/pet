# tutor_dash/views.py  ← TUDO AQUI AGORA
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from pet_app import models
from pet_app.utils import get_tutor_logado
from datetime import date


@login_required
def dash_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    try:
        tutor = models.Tutor.objects.prefetch_related('pet_set').get(id=tutor_data['id'])
        pets = tutor.pet_set.all().order_by('nome')
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return redirect('login')

    context = {
        'tutor': tutor,
        'tutor_data': tutor_data,
        'pets': pets,
    }
    return render(request, 'dash_tutor.html', context)


@login_required
def detalhes_pet(request,pet_id):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    pet = get_object_or_404(models.Pet, id=pet_id, tutor__id=tutor_data['id'])
    proxima_consulta = pet.agendamento_set.filter(data__gte=date.today()).order_by('data').first()

    context = {
        'pet': pet,
        'tutor': models.Tutor.objects.get(id=tutor_data['id']),
        'proxima_consulta': proxima_consulta,
    }
    return render(request, 'pet_detalhes.html', context)


@login_required
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
    return render(request, 'tutor_perfil.html', context)


@login_required
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

        # Contatos
        models.ContatoTutor.objects.filter(id_tutor=tutor.id).delete()
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')

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