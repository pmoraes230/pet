from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("pet_app.urls")),           
    path("tutor_dash/", include("tutor_dash.urls")),  # URLs do tutor
    path("vet_dash/", include("vet_dash.urls")),  # URLs do veterinário
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
