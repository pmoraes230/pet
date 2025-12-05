from django.urls import path
from . import views

urlpatterns = [
    path("dash_tutor/", views.dash_tutor, name="dash_tutor"),
    path("perfil_tutor/", views.perfil_tutor, name="perfil_tutor"),
    path("edicao_perfil_tutor/", views.editar_perfil_tutor, name="edicao_perfil_tutor")
]
