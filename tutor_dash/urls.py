from django.urls import path
from . import views

urlpatterns = [
    path("perfil_tutor/", views.perfil_tutor, name="perfil_tutor"),
    path("edicao_perfil_tutor/", views.editar_perfil_tutor, name="edicao_perfil_tutor"),
    path('config_tutor/', views.config_tutor, name="config_tutor"),
    path("desativar_conta/", views.desativar_conta, name="desativar_conta"),
    path('dash_tutor/', views.tutor_dashboard_view, name='tutor_dash'),
    path('meus-pets/', views.meus_pets, name='meus_pets'),
    # path('edicao_perfil_tutor/'),
    path('adicionar-pet/', views.adicionar_pet, name='adicionar_pet'),
    path('excluir-pet/<int:pet_id>/', views.excluir_pet, name='excluir_pet'),
    path('pet/<int:pet_id>/', views.detalhe_pet, name='detalhe_pet'),
    path('adicionar-pet/', views.adicionar_pet, name='adicionar_pet'),
    path('medicamentos/', views.medicamentos_view, name='medicamentos'),
    path('agendamentos/', views.agendamentos_view, name='agendamentos'),
    path('excluir-consulta/<int:consulta_id>/', views.excluir_consulta, name='excluir_consulta'),
    path('excluir-vacina/<int:vacina_id>/', views.excluir_vacina, name='excluir_vacina'),
    path('diario-emocional/', views.diario_emocional_view, name='diario_emocional'),
    
]
