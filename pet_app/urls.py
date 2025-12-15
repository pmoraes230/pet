from django.urls import path
from . import views

urlpatterns = [
    # ==================================================
    # PÁGINA INICIAL / AUTENTICAÇÃO
    # ==================================================
    path("", views.home, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("insert-tutor-ajax/", views.insert_tutor_ajax, name="insert_tutor_ajax"),

    # ==================================================
    # DASHBOARDS
    # ==================================================
    path("tutor_dash/", views.tutor_dashboard_view, name="tutor_dashboard"),
    path("vet_dash/", views.vet_dashboard_view, name="vet_dashboard"),

    # ==================================================
    # ÁREA DO TUTOR
    # ==================================================
    path("perfil-tutor/", views.perfil_tutor, name="perfil_tutor"),
    path("editar-perfil-tutor/", views.editar_perfil_tutor, name="editar_perfil_tutor"),

    # Pets
    path("meus-pets/", views.meus_pets, name="meus_pets"),
    path("adicionar-pet/", views.adicionar_pet, name="adicionar_pet"),
    path("excluir-pet/<int:pet_id>/", views.excluir_pet, name="excluir_pet"),

    # ==================================================
    # ÁREA DO VETERINÁRIO
    # ==================================================
    path("perfil-veterinario/", views.perfil_veterinario, name="perfil_veterinario"),
    path("editar-perfil-veterinario/", views.editar_perfil_veterinario, name="editar_perfil_veterinario"),
]
