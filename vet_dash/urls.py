from django.urls import path
from . import views

urlpatterns = [
    path("dash_vet/", views.dash_vet, name="dash_vet")
]
