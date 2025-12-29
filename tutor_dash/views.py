


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
    return render(request, 'dash_tutor.html', context)


# ========================================================
# PERFIL DO TUTOR
# ========================================================

def perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    contatos = models.ContatoTutor.objects.filter(tutor=tutor)

    return render(request, 'tutor_perfil.html', {
        'tutor': tutor,
        'contatos': contatos
    })


def editar_perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    contatos = models.ContatoTutor.objects.filter(tutor=tutor)

    if request.method == "POST":
        tutor.nome_tutor = request.POST.get('nome_tutor')
        tutor.cpf = request.POST.get('cpf')
        tutor.data_nascimento = request.POST.get('data_nascimento')
        tutor.endereco = request.POST.get('endereco')

        if request.FILES.get('image_tutor'):
            tutor.imagem_perfil_tutor = request.FILES['image_tutor']

        tutor.save()

        models.ContatoTutor.objects.filter(tutor=tutor).delete()

        tipos = request.POST.getlist('tipo_contato')
        ddds = request.POST.getlist('ddd')
        numeros = request.POST.getlist('numero')

        for i in range(len(tipos)):
            if ddds[i] and numeros[i]:
                models.ContatoTutor.objects.create(
                    tutor=tutor,
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


from django.shortcuts import render, redirect
from django.contrib import messages
from pet_app import models
from pet_app.utils import get_tutor_logado


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

    pet = models.Pet.objects.filter(
        id=pet_id,
        tutor=tutor
    ).first()

    if pet:
        pet.delete()
        messages.success(request, "Pet removido com sucesso!")
    else:
        messages.error(request, "Pet não encontrado.")

    return redirect('meus_pets')

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Pet, Consulta # Certifique-se de importar suas models
from datetime import date

def detalhe_pet(request, pet_id):
    # Busca o pet ou retorna 404
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == "POST":
        # 1. Campos básicos (que você já tinha)
        pet.nome = request.POST.get('nome')
        pet.especie = request.POST.get('especie')
        pet.raca = request.POST.get('raca')
        pet.sexo = request.POST.get('sexo')
        pet.pelagem = request.POST.get('pelagem')
        pet.castrado = request.POST.get('castrado')

        # 2. Novos campos (conforme o layout e o banco que você alterou)
        pet.peso = request.POST.get('peso')
        pet.descricao = request.POST.get('descricao')
        pet.personalidade = request.POST.get('personalidade') # Captura a string das tags do modal

        # 3. Verificação de upload de imagem
        if 'imagem' in request.FILES:
            pet.imagem = request.FILES['imagem']

        # Salva todas as alterações no banco
        pet.save()
        return redirect('detalhe_pet', pet_id=pet.id)

    # --- LÓGICA PARA O MODO "GET" (Carregamento da página) ---

    # Transforma a string "Brincalhão,Guloso" em uma lista ['Brincalhão', 'Guloso']
    # Isso permite que o HTML faça o loop para criar os quadradinhos amarelos
    list_personalidades = []
    if pet.personalidade:
        list_personalidades = pet.personalidade.split(',')

    # Busca a próxima consulta agendada para este pet (para o card roxo)
    proxima_consulta = Consulta.objects.filter(
        pet=pet, 
        data_consulta__gte=date.today()
    ).order_by('data_consulta').first()

    # Busca as vacinas (Se você criou a tabela vacina no passo anterior)
    # Se ainda não criou, deixe como uma lista vazia por enquanto: vacinas = []
    try:
        from .models import Vacina
        vacinas = Vacina.objects.filter(pet=pet).order_by('-data_aplicacao')
    except ImportError:
        vacinas = []

    context = {
        'pet': pet,
        'list_personalidades': list_personalidades,
        'proxima_consulta': proxima_consulta,
        'vacinas': vacinas,
    }

    return render(request, 'detalhe_pet.html', context)

