from django.db import models
from django.contrib.auth.models import User

class Pet(models.Model):
    dono = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    raca = models.CharField(max_length=100)
    idade = models.IntegerField()
    foto = models.ImageField(upload_to='pets/', null=True, blank=True)

    def __str__(self):
        return self.nome