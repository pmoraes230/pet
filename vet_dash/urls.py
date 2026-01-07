from django.urls import path
from . import views

urlpatterns = [
    path('', views.dash_veterinario, name='dash_veterinario'),
    path('perfil/', views.perfil_veterinario, name='perfil_veterinario'),
    path('perfil/editar/', views.editar_perfil_veterinario, name='edicao_perfil_veterinario'),
    path('pacientes/', views.pacientes_view, name='pacientes_url'),
    path('agenda/', views.agenda_view, name='agenda_url'),            # Adicionado
    path('prontuarios/', views.prontuarios_view, name='prontuarios_url'), # Adicionado
    path('financeiro/', views.financeiro_view, name='financeiro_url'), # Adicionado
    path('pacientes/<int:pet_id>/', views.detalhe_pet_view, name='detalhes_pet'),
    
]

