from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views import View  # se usar no futuro
from pet_app import models
from pet_app.utils import get_tutor_logado, get_veterinario_logado
from django.urls import reverse
import json
from datetime import date, timedelta, datetime
from pet_app.models import Tutor, Pet, Vacina, Consulta, DiarioEmocional
from pet_app import models as pet_models


# Create your views here.
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
    return render(request, 'dash_tutor/dash_tutor.html', context)


# ========================================================
# PERFIL DO TUTOR
# ========================================================

def perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])

    return render(request, 'edit_tutor/tutor_perfil.html', {
        'tutor': tutor,
        # 'contatos': contatos,  # Descomente quando o modelo existir
    })


def editar_perfil_tutor(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    # contatos = models.ContatoTutor.objects.filter(id_tutor=tutor).order_by('-data_cadastro')

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
        # models.ContatoTutor.objects.filter(id_tutor=tutor.id).delete()

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
        # 'contatos': contatos,
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

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    data_url = request.GET.get('data')
    if data_url:
        try:
            hoje_referencia = datetime.strptime(data_url, '%Y-%m-%d').date()
        except ValueError:
            hoje_referencia = date.today()
    else:
        hoje_referencia = date.today()

    segunda_da_semana = hoje_referencia - timedelta(days=hoje_referencia.weekday())
    
    data_semana_anterior = segunda_da_semana - timedelta(days=7)
    data_semana_proxima = segunda_da_semana + timedelta(days=7)

    dias_semana = []
    nomes_curtos = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']
    hoje_real = date.today()
    
    for i in range(7):
        dia_iterado = segunda_da_semana + timedelta(days=i)
        dias_semana.append({
            'nome': nomes_curtos[i],
            'num': dia_iterado.day,
            'hoje': dia_iterado == hoje_real,
            'data_full': dia_iterado
        })

    fim_da_semana = segunda_da_semana + timedelta(days=6)
    vacinas = models.Vacina.objects.filter(pet__in=pets, data_aplicacao__range=[segunda_da_semana, fim_da_semana])
    consultas = models.Consulta.objects.filter(pet__in=pets, data_consulta__range=[segunda_da_semana, fim_da_semana])

    meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho',
             7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}

    context = {
        'tutor': tutor,
        'dias_semana': dias_semana,
        'vacinas': vacinas,
        'consultas': consultas,
        'mes_atual': meses[segunda_da_semana.month],
        'ano_atual': segunda_da_semana.year,
        'data_anterior': data_semana_anterior.strftime('%Y-%m-%d'),
        'data_proxima': data_semana_proxima.strftime('%Y-%m-%d'),
    }
    return render(request, 'agendamentos.html', context)
    # Removido o return duplicado

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
            TUTOR=tutor
        )

        messages.success(request, "Pet cadastrado com sucesso!")
        return redirect('meus_pets')

    return render(request, 'form_pet.html', {'tutor': tutor})

def excluir_pet(request, pet_id):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pet = models.Pet.objects.filter(id=pet_id, tutor=tutor).first()

    if pet:
        pet.delete()
        messages.success(request, "Pet removido com sucesso!")
    else:
        messages.error(request, "Pet não encontrado.")

    return redirect('meus_pets')


class PetDetailView(View):
    template_name = 'detalhe_pet.html'  # ajuste se necessário

    def get(self, request, pet_id):
        pet = self._get_pet(pet_id)
        context = self._prepare_context(pet, request)
        return render(request, self.template_name, context)

    def post(self, request, pet_id):
        pet = self._get_pet(pet_id)

        # 1. Verifica se veio dados de vacina (campos hidden preenchidos via JS)
        nome_vacina = request.POST.get('nome_vacina', '').strip()
        data_aplicacao = request.POST.get('data_aplicacao', '').strip()

        if nome_vacina and data_aplicacao:
            # Prioridade: se veio vacina → cria a vacina e ignora update do pet
            self._add_vacina(pet, request.POST)
            # Opcional: messages.success(request, "Vacina registrada com sucesso!")
            return redirect('detalhe_pet', pet_id=pet.id)

        # 2. Senão → trata como atualização normal do pet
        self._update_pet(pet, request.POST, request.FILES)
        # Opcional: messages.success(request, "Dados do pet atualizados!")
        return redirect('detalhe_pet', pet_id=pet.id)

    def _get_pet(self, pet_id):
        return get_object_or_404(models.Pet, id=pet_id)

    def _prepare_context(self, pet, request):
        list_personalidades = pet.personalidade.split(',') if pet.personalidade else []
        proxima_consulta = models.Consulta.objects.filter(
            pet=pet,
            data_consulta__gte=date.today()
        ).order_by('data_consulta').first()

        vacinas = models.Vacina.objects.filter(pet=pet).order_by('-data_aplicacao')

        return {
            'pet': pet,
            'list_personalidades': list_personalidades,
            'proxima_consulta': proxima_consulta,
            'vacinas': vacinas,
            'tutor': get_tutor_logado(request)
        }

    def _add_vacina(self, pet, post_data):
        """Cria vacina se os campos mínimos vierem preenchidos"""
        models.Vacina.objects.create(
            nome=post_data.get('nome_vacina', '').strip(),
            data_aplicacao=post_data.get('data_aplicacao'),
            proxima_dose=post_data.get('proxima_dose') or None,
            pet=pet
        )

    def _update_pet(self, pet, post_data, files):
        """Atualiza campos do pet (usando ORM por simplicidade e segurança)"""
        pet.nome = post_data.get('nome', pet.nome).strip()
        pet.especie = post_data.get('especie', pet.especie).strip()
        pet.raca = post_data.get('raca', pet.raca).strip()
        pet.sexo = post_data.get('sexo', pet.sexo)
        pet.pelagem = post_data.get('pelagem', pet.pelagem)  # se existir no form
        pet.descricao = post_data.get('descricao', pet.descricao or '').strip()

        # Personalidade vem como string separada por vírgula
        personalidade = post_data.get('personalidade', '').strip()
        if personalidade:
            pet.personalidade = personalidade
        # senão mantém o valor anterior (não apaga)

        # Peso - trata com cuidado
        peso_raw = post_data.get('peso', '').strip().replace(',', '.')
        if peso_raw:
            try:
                pet.peso = float(peso_raw)
            except ValueError:
                pet.peso = pet.peso  # mantém anterior se inválido
        else:
            pet.peso = None

        # Imagem
        if 'imagem' in files and files['imagem']:
            pet.imagem = files['imagem']

        pet.save()

        # Se quiser manter o SQL raw como antes, substitua o bloco acima por:
        # self._update_pet_sql(pet, post_data, files)

# ========================================================
# MEDICAMENTOS / AGENDAMENTOS
# ========================================================

def medicamentos_view(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    hoje = date.today()
    atendimentos_hoje = models.Consulta.objects.filter(
        pet__in=pets,
        data_consulta=hoje
    ).exclude(tratamento__isnull=True).exclude(tratamento='')

    meds_manha = [m for m in atendimentos_hoje if m.horario_consulta and m.horario_consulta.hour < 12]
    meds_tarde = [m for m in atendimentos_hoje if m.horario_consulta and 12 <= m.horario_consulta.hour < 18]
    meds_noite = [m for m in atendimentos_hoje if m.horario_consulta and m.horario_consulta.hour >= 18]

    tratamentos_ativos = models.Consulta.objects.filter(
        pet__in=pets,
        data_consulta__gte=hoje
    ).exclude(tratamento__isnull=True).exclude(tratamento='').order_by('data_consulta')

    context = {
        'tutor': tutor,
        'meds_manha': meds_manha,
        'meds_tarde': meds_tarde,
        'meds_noite': meds_noite,
        'tratamentos_ativos': tratamentos_ativos,
    }
    return render(request, 'medicamentos.html', context)


def agendamentos_view(request):
    # Usando sua função utilitária ou lógica de pegar o ID do tutor logado
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    # CORREÇÃO: Usamos pet_models.Tutor (com o prefixo correto)
    tutor = pet_models.Tutor.objects.get(id=tutor_data['id'])
    
    # Buscamos os pets do tutor
    meus_pets = pet_models.Pet.objects.filter(tutor=tutor)

    # Lógica de calendário
    data_url = request.GET.get('data')
    if data_url:
        try:
            hoje_referencia = datetime.strptime(data_url, '%Y-%m-%d').date()
        except ValueError:
            hoje_referencia = date.today()
    else:
        hoje_referencia = date.today()

    segunda_da_semana = hoje_referencia - timedelta(days=hoje_referencia.weekday())
    
    dias_semana = []
    nomes_curtos = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']
    for i in range(7):
        dia_iterado = segunda_da_semana + timedelta(days=i)
        dias_semana.append({
            'nome': nomes_curtos[i],
            'num': dia_iterado.day,
            'hoje': dia_iterado == date.today(),
            'data_full': dia_iterado
        })

    fim_da_semana = segunda_da_semana + timedelta(days=6)
    
    # CORREÇÃO: Usamos pet_models para buscar Vacinas e Consultas
    vacinas = pet_models.Vacina.objects.filter(
        pet__in=meus_pets, 
        data_aplicacao__range=[segunda_da_semana, fim_da_semana]
    )
    consultas = pet_models.Consulta.objects.filter(
        pet__in=meus_pets, 
        data_consulta__range=[segunda_da_semana, fim_da_semana]
    )

    meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho',
             7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}

    context = {
        'tutor': tutor,
        'dias_semana': dias_semana,
        'vacinas': vacinas,
        'consultas': consultas,
        'mes_atual': meses[segunda_da_semana.month],
        'ano_atual': segunda_da_semana.year,
        'data_anterior': (segunda_da_semana - timedelta(days=7)).strftime('%Y-%m-%d'),
        'data_proxima': (segunda_da_semana + timedelta(days=7)).strftime('%Y-%m-%d'),
        
        # ESSENCIAL PARA O MODAL:
        'pets': meus_pets, 
        'veterinarios': pet_models.Veterinario.objects.all(),
    }
    return render(request, 'agendamentos.html', context)
    # Removido o return duplicado


def diario_emocional_view(request):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    pets = models.Pet.objects.filter(tutor=tutor)

    if request.method == "POST":
        pet_id = request.POST.get('pet_id')
        humor = request.POST.get('humor')
        relato = request.POST.get('relato')

        if not humor:
            messages.error(request, "Por favor, selecione um emoji de humor!")
        elif not relato:
            messages.error(request, "Escreva um pequeno relato sobre o pet.")
        else:
            try:
                models.DiarioEmocional.objects.create(
                    pet_id=pet_id,
                    humor=int(humor),
                    relato=relato
                )
                messages.success(request, "Comportamento registrado com sucesso!")
                return redirect('diario_emocional')
            except Exception as e:
                messages.error(request, "Erro técnico ao salvar no banco.")

    pet_selecionado = pets.first()
    recentes = models.DiarioEmocional.objects.filter(pet__in=pets).order_by('-data_registro')[:5]

    labels = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
    if pet_selecionado:
        registros = models.DiarioEmocional.objects.filter(pet=pet_selecionado).order_by('-data_registro')[:7]
        valores = [r.humor for r in reversed(registros)]
    else:
        valores = []

    while len(valores) < 7:
        valores.insert(0, 2)  # valor neutro

    return render(request, 'diario_emocional.html', {
        'pets': pets,
        'recentes': recentes,
        'pet_selecionado': pet_selecionado,
        'grafico_labels': json.dumps(labels),
        'grafico_valores': json.dumps(valores)
    })


from django.shortcuts import render, get_object_or_404, redirect
from pet_app.models import Pet, Vacina, Consulta # Import correto agora
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from pet_app.models import Pet, Vacina, Consulta # Importando do app correto
from django.utils import timezone

def perfil_pet(request, pet_id):
    # 1. Busca o pet
    pet = get_object_or_404(Pet, id=pet_id)
    
    # 2. Se for POST, salva as alterações
    if request.method == "POST":
        # Usamos 'or pet.campo' para que se o campo vier vazio, ele não salve como None
        pet.nome = request.POST.get('nome') or pet.nome
        pet.peso = request.POST.get('peso') or pet.peso
        pet.sexo = request.POST.get('sexo') or pet.sexo
        pet.descricao = request.POST.get('descricao') or pet.descricao
        pet.especie = request.POST.get('especie') or pet.especie
        pet.raca = request.POST.get('raca') or pet.raca
        pet.personalidade = request.POST.get('personalidade') or pet.personalidade

        # Tratamento de imagem
        if request.FILES.get('imagem'):
            pet.imagem = request.FILES.get('imagem')

        pet.save()
        # Após salvar, redireciona para a mesma página para limpar o POST
        return redirect('perfil_pet', pet_id=pet.id)

    # 3. Dados para exibição (fora do IF POST para carregar sempre)
    vacinas = Vacina.objects.filter(id_pet=pet.id)
    proxima_consulta = Consulta.objects.filter(
        id_pet=pet.id, 
        data_consulta__gte=timezone.now().date()
    ).order_by('data_consulta').first()

    # Transforma a string de personalidade em lista para as tags
    list_personalidades = []
    if pet.personalidade:
        list_personalidades = [p.strip() for p in pet.personalidade.split(',') if p.strip()]

    context = {
        'pet': pet,
        'vacinas': vacinas,
        'proxima_consulta': proxima_consulta,
        'list_personalidades': list_personalidades,
    }
    
    return render(request, 'perfil_pet.html', context)


# ========================================================
# EXCLUSÃO DE AGENDAMENTOS (CONSULTAS E VACINAS)
# ========================================================

def excluir_consulta(request, consulta_id):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    consulta = models.Consulta.objects.filter(id=consulta_id, pet__tutor=tutor).first()

    if consulta:
        consulta.delete()
        messages.success(request, "Agendamento removido com sucesso!")
    else:
        messages.error(request, "Agendamento não encontrado.")

    return redirect('agendamentos')


def excluir_vacina(request, vacina_id):
    tutor_data = get_tutor_logado(request)
    if not tutor_data:
        return redirect('login')

    tutor = models.Tutor.objects.get(id=tutor_data['id'])
    vacina = models.Vacina.objects.filter(id=vacina_id, pet__tutor=tutor).first()

    if vacina:
        vacina.delete()
        messages.success(request, "Registro de vacinação removido com sucesso!")
    else:
        messages.error(request, "Registro não encontrado.")

    return redirect('agendamentos')

from datetime import datetime # Certifique-se de que este import está no topo do arquivo

from datetime import datetime
from django.shortcuts import get_object_or_404, redirect


def agendar_consulta(request):
    if request.method == 'POST':
        pet_id = request.POST.get('pet')
        vet_id = request.POST.get('veterinario')
        data_str = request.POST.get('data')
        hora = request.POST.get('hora')
        tipo = request.POST.get('tipo')
        obs = request.POST.get('obs')

        # 1. Busca as instâncias do Pet e Veterinário
        pet_obj = get_object_or_404(models.Pet, id=pet_id)
        vet_obj = get_object_or_404(models.Veterinario, id=vet_id)

        # 2. Converte a string de data para um objeto date (evita erro no Signal)
        try:
            data_objeto = datetime.strptime(data_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            data_objeto = None # Ou use datetime.now().date()

        # 3. Cria o registro seguindo EXATAMENTE os nomes do seu modelo
        models.Consulta.objects.create(
            tipo_de_consulta=tipo,
            data_consulta=data_objeto,
            horario_consulta=hora,
            # Limitamos a 255 caracteres para bater com o max_length do seu CharField
            observacoes=obs[:255] if obs else None, 
            status='Agendado',
            pet=pet_obj,        # Atributo definido no seu model
            veterinario=vet_obj # Atributo definido no seu model
        )

        return redirect('agendamentos')
    
    return redirect('agendamentos')
    

# Função para excluir consulta
def excluir_consulta(request, id):
    consulta = get_object_or_404(models.Consulta, id=id)
    consulta.delete()
    return redirect('agendamentos')

# Função para excluir vacina
def excluir_vacina(request, id):
    vacina = get_object_or_404(models.Vacina, id=id)
    vacina.delete()
    return redirect('agendamentos')