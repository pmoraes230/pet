from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from pet_app import models
from pet_app.utils import get_tutor_logado

# ========================================================
# DASHBOARD DO TUTOR
# ========================================================

def tutor_dashboard_view(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)  # ✅ Correção

    proxima_consulta = models.Consulta.objects.filter(
        id_pet__in=pets,  # ✅ Usa id_pet do modelo Consulta
        data_consulta__gte=date.today()
    ).order_by('data_consulta', 'horario_consulta').first()

    historico_recente = models.Consulta.objects.filter(
        id_pet__in=pets  # ✅ Usa id_pet
    ).order_by('-data_consulta', '-horario_consulta')[:5]

    context = {
        'tutor': tutor,
        'pets': pets,
        'proxima_consulta': proxima_consulta,
        'historico_recente': historico_recente,
        'total_pets': pets.count()
    }
    return render(request, 'dash_tutor.html', context)


# ========================================================
# PERFIL DO TUTOR
# ========================================================

def perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    contatos = models.ContatoTutor.objects.filter(id_tutor=tutor)  # ✅ Correção

    return render(request, 'tutor_perfil.html', {
        'tutor': tutor,
        'contatos': contatos
    })


def editar_perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    contatos = models.ContatoTutor.objects.filter(id_tutor=tutor)

    if request.method == "POST":
        tutor.nome_tutor = request.POST.get('nome_tutor')
        tutor.cpf = request.POST.get('cpf')
        tutor.data_nascimento = request.POST.get('data_nascimento')
        tutor.endereco = request.POST.get('endereco')

        if request.FILES.get('image_tutor'):
            tutor.imagem_perfil_tutor = request.FILES['image_tutor']

        tutor.save()

        # Atualiza contatos
        models.ContatoTutor.objects.filter(id_tutor=tutor).delete()
        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')

        for i in range(len(tipos)):
            if ddds[i] and numeros[i]:
                models.ContatoTutor.objects.create(
                    id_tutor=tutor,
                    tipo_contato=tipos[i],
                    ddd=ddds[i],
                    numero=numeros[i]
                )

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('perfil_tutor')

    return render(request, 'editar_perfil.html', {
        'tutor': tutor,
        'contatos': contatos
    })


# ========================================================
# PETS
# ========================================================

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

    tutor = models.Tutor.objects.get(id=tutor_data['id'])

    if request.method == "POST":
        nome = request.POST.get('nome')

        prontuario = models.ProntuarioPet.objects.create(
            historico_veterinario=f"Prontuário inicial de {nome}",
            motivo_consulta="Cadastro",
            avaliacao_geral="-",
            procedimentos="-",
            diagnostico_conslusivo="-",
            observacao="-"
        )

        models.Pet.objects.create(
            nome=nome,
            especie=request.POST.get('especie'),
            raca=request.POST.get('raca'),
            data_nascimento=request.POST.get('data_nascimento'),
            sexo=request.POST.get('sexo'),
            pelagem=request.POST.get('pelagem', 'Não informada'),
            castrado=request.POST.get('castrado', 'Não'),
            tutor=tutor,  # ✅ Correção
            id_consulta=prontuario  # ✅ Corrigido
        )

        messages.success(request, "Pet cadastrado com sucesso!")
        return redirect('meus_pets')

    return render(request, 'adicionar_pet.html', {'tutor': tutor})


def excluir_pet(request, pet_id):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    pet = models.Pet.objects.filter(
        id=pet_id,
        tutor=tutor_data['id']  # ✅ Correção: usa tutor
    ).first()

    if pet:
        pet.delete()
        messages.success(request, "Pet removido com sucesso!")
    else:
        messages.error(request, "Pet não encontrado.")

    return redirect('meus_pets')
