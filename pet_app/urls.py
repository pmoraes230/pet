from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="index"),
    path("login/", views.login_page, name="login")
]
