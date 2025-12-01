from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("pet_app.urls")),
    path("tutor_dash/", include("tutor_dash.urls")),
    path("vet_dash/", include("vet_dash.urls"))
]
