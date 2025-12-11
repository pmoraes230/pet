# tutor_dash/urls.py
from django.urls import path
from . import views  # ← agora pega do tutor_dash.views (onde você acabou de colar)

urlpatterns = [
    path("", views.dash_tutor, name="dash_tutor"),
    path("dash_tutor/", views.dash_tutor, name="dash_tutor"),
    path("pet/<int:pet_id>/", views.detalhes_pet, name="detalhes_pet"),
    path("perfil_tutor/", views.perfil_tutor, name="perfil_tutor"),
    path("edicao_perfil_tutor/", views.editar_perfil_tutor, name="edicao_perfil_tutor"),
]