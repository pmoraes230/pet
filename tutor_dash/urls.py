from django.urls import path
from . import views

urlpatterns = [
    path('', views.tutor_dashboard_view, name='tutor_dash'),
    path('meus-pets/', views.meus_pets, name='meus_pets'),
    path('adicionar-pet/', views.adicionar_pet, name='adicionar_pet'),
    path('excluir-pet/<int:pet_id>/', views.excluir_pet, name='excluir_pet'),
    path('pet/<int:pet_id>/', views.detalhe_pet, name='detalhe_pet'),
    path('adicionar-pet/', views.adicionar_pet, name='adicionar_pet'),
]
