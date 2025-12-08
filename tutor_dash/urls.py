# tutor_dash/urls.py
from django.urls import path
from . import views  # Certifique-se de que você está importando as views corretamente

urlpatterns = [
    path('dash_tutor/', views.dash_tutor, name='dash_tutor'),
    path('perfil_tutor/', views.perfil_tutor, name='perfil_tutor'),  # Verifique o nome aqui
    path('editar_perfil/', views.editar_perfil_tutor, name='editar_perfil'),
]
