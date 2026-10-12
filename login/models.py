from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)
    documento = models.CharField(max_length=255, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    def __str__(self):
        return self.user.username