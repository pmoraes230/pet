from django.urls import path
from . import views

urlpatterns = [
    path("dash_veterinario/", views.dash_veterinario, name="dash_veterinario"),
    path("perfil_veterinario/", views.perfil_veterinario, name="perfil_veterinario"),
    path("edicao_perfil_veterinario/", views.editar_perfil_veterinario, name="edicao_perfil_veterinario"),
]
