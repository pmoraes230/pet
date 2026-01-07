from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required  # se usar no futuro
from pet_app import models
from pet_app.utils import get_tutor_logado
import json
from datetime import date, timedelta, datetime

# Create your views here.
def dash_tutor(request):
    if request.session.get('user_role') != 'tutor':
        return redirect('login')

    tutor_id = request.session['user_id']
    
    try:
        tutor = models.Tutor.objects.get(id=tutor_id)
    except models.Tutor.DoesNotExist:
        return redirect('login')

    # Pegamos os pets normalmente
    pets_qs = models.Pet.objects.filter(id_tutor=tutor_id).order_by('nome')

    # Convertemos manualmente para dicionário SEM passar ImageField ou qualquer objeto não serializável
    pets = []
    for pet in pets_qs:
        pets.append({
            "id": pet.id,
            "nome": pet.nome,
            "especie": pet.especie,
            "raca": pet.raca or "Não informada",
            "sexo": pet.sexo,
            "pelagem": pet.pelagem or "Não informada",
            "castrado": pet.castrado == "Sim",
            "data_nascimento": pet.data_nascimento.isoformat() if pet.data_nascimento else None,
            "idade": pet.calcular_idade() if hasattr(pet, 'calcular_idade') else None,
            # Foto gerada automaticamente (sem campo no banco!)
            "foto": f"https://api.dicebear.com/7.x/avataaars/svg?seed=pet-{pet.id}&backgroundColor=ffdfbf,b6e3f4,c0a5ff,d1d4f9"
        })

    context = {
        "tutor": {
            "nome": tutor.nome_tutor or "Tutor",
            "email": tutor.email,
        },
        "pets": pets,  # ← 100% serializável, sem ImageFieldFile!
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

    # ATENÇÃO: ContatoTutor NÃO existe nos models que você me mostrou
    # Se esse modelo existe em outro app ou foi esquecido, adicione-o.
    # Por enquanto, comento para não dar erro:
    # contatos = ContatoTutor.objects.filter(tutor=tutor)  # <-- ERRO SE NÃO EXISTIR

    return render(request, 'tutor_perfil.html', {
        'tutor': tutor,
        # 'contatos': contatos,  # Descomente quando o modelo existir
    })


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

# class ContatoTutor(models.Model):
#     id = models.AutoField(db_column='ID', primary_key=True)
#     tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='ID_TUTOR')
#     tipo_contato = models.CharField(db_column='TIPO_CONTATO', max_length=16, blank=True, null=True)
#     ddd = models.CharField(db_column='DDD', max_length=2, blank=True, null=True)
#     numero = models.CharField(db_column='NUMERO', max_length=9, blank=True, null=True)
#     data_cadastro = models.DateTimeField(db_column='DATA_CADASTRO', blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'contato_tutor'

#     def __str__(self):
#         return f"{self.tipo_contato} {self.ddd}{self.numero} - {self.tutor}"
