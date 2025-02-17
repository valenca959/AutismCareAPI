from django.db import models
from django.contrib.auth.models import AbstractUser

class AutenticationUser(AbstractUser):
    telephone = models.CharField(max_length=15)
    telephone2 = models.CharField(max_length=15, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    cpf = models.CharField(max_length=11)

    def __str__(self):
        return self.username
    
