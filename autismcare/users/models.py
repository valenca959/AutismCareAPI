# autismcare/users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.core.validators import RegexValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

class Address(models.Model):
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=9)
    country = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}/{self.state}"

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

class AutenticationUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
    address = models.OneToOneField(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user"
    )
    telephone = PhoneNumberField(region="BR")
    telephone2 = PhoneNumberField(blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(r'^\d{11}$', 'CPF deve ter 11 dígitos numéricos.')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cpf']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_user_type(self):
        if hasattr(self, 'employee'):
            return 'employee'
        elif hasattr(self, 'parent'):
            return 'parent'
        return 'autentication_user'

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['cpf']),
        ]


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nome da Role")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name="Permissões"
    )
    parent_role = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Role Superior"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ["name"]

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('terminated', 'Demitido'),
    ]

    user = models.OneToOneField(
        AutenticationUser,
        on_delete=models.CASCADE,
        related_name='employee'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Função"
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    admission_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'Sem função'}"