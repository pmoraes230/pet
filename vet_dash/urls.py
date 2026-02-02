from django.urls import path
from . import views

urlpatterns = [
    path('', views.dash_veterinario, name='dash_veterinario'),
    path('perfil/', views.perfil_veterinario, name='perfil_veterinario'),
    path('perfil/editar/', views.editar_perfil_veterinario, name='edicao_perfil_veterinario'),
    path('pacientes/', views.pacientes_view, name='pacientes_url'),
    path('agenda/', views.agenda_view, name='agenda_vet'),
    path('prontuarios/', views.prontuarios_view, name='prontuarios_url'),
    path('financeiro/', views.financeiro_view, name='financeiro_url'),
    path('mensagens/', views.mensagens_vet, name='mensagens_vet'),
    path('mensagens/enviar/', views.enviar_mensagem_vet, name='enviar_mensagem_vet'),
    path('pacientes/<uuid:pet_id>/', views.detalhe_pet_view, name='detalhes_pet'),
    path('pacientes/<uuid:pet_id>/perfil/', views.perfil_pet_vet, name='perfil_pet_vet'),
    path('excluir-consulta/<uuid:consulta_id>/', views.excluir_consulta_vet, name='excluir_consulta_vet'),
    path('excluir-vacina/<uuid:vacina_id>/', views.excluir_vacina_vet, name='excluir_vacina_vet'),
    path('aceitar-consulta/<uuid:consulta_id>/', views.aceitar_consulta, name='aceitar_consulta'),
    path('rejeitar-consulta/<uuid:consulta_id>/', views.rejeitar_consulta, name='rejeitar_consulta'),
    path('notificacoes/historico/', views.historico_notificacao_vet, name='historico_notificacao_vet'),
]

