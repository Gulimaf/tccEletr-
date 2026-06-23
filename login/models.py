from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username