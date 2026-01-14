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

from .models import Notificacao

def notificacoes_context(request):
    # 1. Pegamos os nomes EXATOS que você usa no login e no utils
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role') # Mudamos de user_tipo para user_role

    if user_id and user_role:
        if user_role == 'tutor':
            # Notificações para o Tutor
            notifs = Notificacao.objects.filter(tutor_id=user_id)
        elif user_role == 'vet': # Mudamos para 'vet' conforme seu utils
            # Notificações para o Veterinário
            notifs = Notificacao.objects.filter(veterinario_id=user_id)
        else:
            return {}

        return {
            'notificacoes': notifs.order_by('-data_criacao')[:5], 
            'notificacoes_nao_lidas_count': notifs.filter(lida=False).count()
        }
    return {}