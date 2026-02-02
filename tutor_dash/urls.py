from django.urls import path
from . import views

urlpatterns = [
    # Perfil e Configurações
    path("perfil_tutor/", views.perfil_tutor, name="perfil_tutor"),
    path("edicao_perfil_tutor/", views.editar_perfil_tutor, name="edicao_perfil_tutor"),
    path('config_tutor/', views.config_tutor, name="config_tutor"),
    path("desativar_conta/", views.desativar_conta, name="desativar_conta"),
    
    # Dashboard e Geral
    path('dash_tutor/', views.tutor_dashboard_view, name='tutor_dash'),
    path('medicamentos/', views.medicamentos_view, name='medicamentos'),
    path('diario-emocional/', views.diario_emocional_view, name='diario_emocional'),

    # Gestão de Pets
    path('meus-pets/', views.meus_pets, name='meus_pets'),
    path('adicionar-pet/', views.adicionar_pet, name='adicionar_pet'),
    path('pet/<uuid:pet_id>/', views.PetDetailView.as_view(), name='detalhe_pet'),
    path('excluir-pet/<uuid:pet_id>/', views.excluir_pet, name='excluir_pet'),

    # Agendamentos (Consultas e Vacinas)
    path('agendamentos/', views.agendamentos_view, name='agendamentos'),
    path('agendamentos/novo/', views.agendar_consulta, name='agendar_consulta'),
    path('agendamentos/excluir-consulta/<uuid:id>/', views.excluir_consulta, name='excluir_consulta'),
    path('agendamentos/excluir-vacina/<uuid:id>/', views.excluir_vacina, name='excluir_vacina'),

    path('notificacoes/historico/', views.historico_notificacoes_tutor, name='historico_notificacoes_tutor'),
]
    
