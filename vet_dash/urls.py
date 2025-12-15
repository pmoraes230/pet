from django.urls import path
from . import views

urlpatterns = [
    path('', views.dash_veterinario, name='dash_veterinario'),
    path('perfil/', views.perfil_veterinario, name='perfil_veterinario'),
    path('perfil/editar/', views.editar_perfil_veterinario, name='edicao_perfil_veterinario'),
]

