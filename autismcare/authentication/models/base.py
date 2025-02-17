from django.db import models
from django.contrib.auth.models import AbstractUser

class AutenticationUser(AbstractUser):
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=9)
    country = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    telephone = models.CharField(max_length=15)
    telephone2 = models.CharField(max_length=15, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return self.username

class Employee(AutenticationUser):
    role = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    admission_date = models.DateField()

    def __str__(self):
        return f"{self.username} - {self.role}"
