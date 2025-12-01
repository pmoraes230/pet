from django.urls import path
from . import views

urlpatterns = [
    path("dash_tutor/", views.dash_tutor, name="dash_tutor"),
]
