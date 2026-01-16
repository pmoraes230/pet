from datetime import datetime

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

from .models import Notificacao

def notificacoes_context(request):
    user_id = request.session.get('user_id')
    user_tipo = request.session.get('user_tipo')

    if user_id and user_tipo:
        if user_tipo == 'tutor':
            # Notificações para o Tutor
            notifs = Notificacao.objects.filter(tutor_id=user_id)
        else:
            # Notificações para o Veterinário
            notifs = Notificacao.objects.filter(veterinario_id=user_id)
        
        return {
            'notificacoes': notifs.order_by('-data_criacao')[:5], # As 5 últimas pro popup
            'notificacoes_nao_lidas_count': notifs.filter(lida=False).count() # Pro contador vermelho
        }
    return {}
