from django.db import connection
from . import models

def call_procedure(proc_name, params):
    with connection.cursor() as cursor:
        cursor.callproc(proc_name, params)
        result = cursor.fetchall()
    return result


def get_tutor_logado(request):
    if request.session.get('user_role') != 'tutor':
        return None
    
    tutor_id = request.session.get('user_id')
    if not tutor_id:
        return None
    
    if 'tutor_obj' in request.session:
        return request.session['tutor_obj']
    
    try:
        tutor = models.Tutor.objects.get(id=tutor_id)
        request.session['tutor_obj'] = {
            'id': tutor.id,
            'nome_tutor': tutor.nome_tutor,
            'email': tutor.email,
            'cpf': tutor.cpf,
            'endereco': tutor.endereco,
            'data_nascimento': tutor.data_nascimento.strftime('%Y-%m-%d') if tutor.data_nascimento else None,
            'imagem_perfil_tutor': tutor.imagem_perfil_tutor.url if tutor.imagem_perfil_tutor else None,
        }
        return request.session['tutor_obj']
    except models.Tutor.DoesNotExist:
        request.session.flush()
        return None


def get_veterinario_logado(request):
    """
    Retorna o objeto Veterinario logado ou None se não estiver logado como veterinário
    """
    if request.session.get('user_role') != 'vet':
        return None
    
    vet_id = request.session.get('user_id')
    if not vet_id:
        return None

    if 'veterinario_obj' in request.session:
        return request.session['veterinario_obj']

    try:
        vet = models.Veterinario.objects.get(id=vet_id)
        request.session['veterinario_obj'] = {
            'id': vet.id,
            'nome': vet.nome,
            'email': vet.email,
            'crmv': vet.crmv,
            'uf_crmv': vet.uf_crmv,
            'telefone': vet.telefone,
            'pessoa_fisica': vet.pessoa_fisica.id if vet.pessoa_fisica else None,
            'pessoa_juridica': vet.pessoa_juridica.id if vet.pessoa_juridica else None,
        }
        return request.session['veterinario_obj']
    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return None
