from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Tutor)
admin.site.register(models.Veterinario)
admin.site.register(models.Pet)
admin.site.register(models.Consulta)
admin.site.register(models.Vacina)