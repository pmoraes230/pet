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
    path('mensagens/', views.mensagens_view, name='mensagens'),
    path('mensagens/enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('esqueci-senha/', views.solicitar_troca_senha, name='solicitar_troca_senha'),
    path('perfil/alterar-senha/', views.alterar_senha_logado, name='alterar_senha_logado'),
    path('recuperar-senha/codigo/', views.inserir_codigo, name='inserir_codigo'),
    path('recuperar-senha/nova/', views.nova_senha, name='nova_senha'),
    path('notificacoes/', views.historico_notificacao, name='historico_notificacao'),

    # Pets
    path("meus-pets/", views.meus_pets, name="meus_pets"),
    path("adicionar-pet/", views.adicionar_pet, name="adicionar_pet"),
    path("excluir-pet/<int:pet_id>/", views.excluir_pet, name="excluir_pet"),

    # ==================================================
    # ÁREA DO VETERINÁRIO
    # ==================================================
    path("perfil-veterinario/", views.perfil_veterinario, name="perfil_vet"),
    path("editar-perfil-veterinario/", views.editar_perfil_veterinario, name="editar_perfil_veterinario"),
    path('notificacoes/', views.lista_notificacoes, name='notificacoes_lista'),
]
