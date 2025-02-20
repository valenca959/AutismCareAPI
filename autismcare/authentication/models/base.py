from django.db import models
from django.contrib.auth.models import AbstractUser

class AutenticationUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cpf']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Employee(AutenticationUser):
    ROLE = [
        ("physiotherapist", "Fisioterapeuta"),
        ("psychologist", "Psicologo"),
        ("pedagogue", "Pedagogo"),
        ("assistant", "Assistente"),
        ("receptionist", "Recepcionista")
    ]
    role = models.CharField(max_length=50, choices=ROLE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    admission_date = models.DateField()

    def __str__(self):
        return f"{self.username} - {self.role}"
