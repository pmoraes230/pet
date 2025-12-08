from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="index"),  # Página inicial
    path("login/", views.login_view, name="login"),  # Login
    path("logout/", views.logout_view, name="logout"),  # Logout correto
    path("register/", views.register_view, name="register"),  # Registro
    path("insert-tutor-ajax/", views.insert_tutor_ajax, name="insert_tutor_ajax"),  # Inserir tutor via AJAX
]
