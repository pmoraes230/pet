from django.db import connection
from django.shortcuts import redirect
from . import models

def call_procedure(proc_name, params):
    with connection.cursor() as cursos:
        cursos.callproc(proc_name, params)
        result = cursos.fetchall()
    return result

def get_tutor_logado(request):
    if not request.session.get('user_role') == 'tutor':
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
            'image_tutor': tutor.imagem_perfil_tutor.url if tutor.imagem_perfil_tutor else None,  # ✔️ Aqui corrigido
        }

        return request.session['tutor_obj']

    except models.Tutor.DoesNotExist:
        request.session.flush()
        return None


def get_veterinario_logado(request):
    """
    Retorna o objeto Veterinario logado ou None se não estiver logado como veterinario
    """
    # Verifica se o usuário logado é veterinário
    if not request.session.get('user_role') == 'veterinario':
        return None
    
    vet_id = request.session.get('user_id')
    if not vet_id:
        return None

    # Cache na própria sessão para evitar query repetida
    if 'veterinario_obj' in request.session:
        return request.session['veterinario_obj']

    try:
        vet = models.Veterinario.objects.get(id=vet_id)

        # Salvar dados serializáveis na sessão
        request.session['veterinario_obj'] = {
            'id': vet.id,
            'nome': vet.nome,
            'email': vet.email,
            'crmv': vet.crmv,
            'uf_crmv': vet.uf_crmv,
            'telefone': vet.telefone,
            'pessoa_fisica': vet.pessoa_fisica_idpessoa_fisica.id if vet.pessoa_fisica_idpessoa_fisica else None,
            'pessoa_juridica': vet.pessoa_juridica_idpessoa_juridica.id if vet.pessoa_juridica_idpessoa_juridica else None,
        }

        return request.session['veterinario_obj']

    except models.Veterinario.DoesNotExist:
        request.session.flush()
        return None
