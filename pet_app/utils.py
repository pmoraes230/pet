from django.db import connection
from django.shortcuts import redirect
from . import models

def call_procedure(proc_name, params):
    with connection.cursor() as cursos:
        cursos.callproc(proc_name, params)
        result = cursos.fetchall()
    return result

def get_tutor_logado(request):
    """
    Retorna o objeto Tutor logado ou None se não estiver logado como tutor
    """
    if not request.session.get('user_role') == 'tutor':
        return None
    
    tutor_id = request.session.get('user_id')
    if not tutor_id:
        return None
    
    # Cache na própria sessão para evitar query repetida
    if 'tutor_obj' in request.session:
        return request.session['tutor_obj']
    
    try:
        tutor = models.Tutor.objects.get(id=tutor_id)
        # Salva no cache da sessão (serializável!)
        request.session['tutor_obj'] = {
            'id': tutor.id,
            'nome_tutor': tutor.nome_tutor,
            'email': tutor.email,
            'cpf': tutor.cpf,
            'endereco': tutor.endereco,
            'data_nascimento': tutor.data_nascimento.strftime('%Y-%m-%d') if tutor.data_nascimento else None,
            'image_tutor': tutor.imagem_perfil_tutor
            # adicione outros campos que você usa com frequência
        }
        return request.session['tutor_obj']
    except models.Tutor.DoesNotExist:
        # Sessão inválida → desloga
        from django.contrib.sessions.models import Session
        request.session.flush()
        return None