from datetime import datetime
from .models import Notificacao

def saudacao_horario(request):
    hora = datetime.now().hour

    if 5 <= hora < 12:
        saudacao = "Bom dia"
    elif 12 <= hora < 18: 
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    return {
        'saudacao_horario': saudacao
    }

def notificacoes(request):
    if not request.user.is_authenticated:
        return {}

    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')

    if user_role == 'vet':
        count = Notificacao.objects.filter(veterinario_id=user_id, lida=False).count()
        notificacoes = Notificacao.objects.filter(veterinario_id=user_id).order_by('-data_criacao')[:5]
    elif user_role == 'tutor':
        count = Notificacao.objects.filter(tutor_id=user_id, lida=False).count()
        notificacoes = Notificacao.objects.filter(tutor_id=user_id).order_by('-data_criacao')[:5]
    else:
        count = 0
        notificacoes = []

    return {
        'notificacoes_nao_lidas_count': count,
        'notificacoes': notificacoes,
    }