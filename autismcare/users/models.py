# autismcare/users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from .fields import EncryptedCharField, hash_cpf

class CustomUserManager(BaseUserManager):
    """
    Gestor de modelo de utilizador personalizado onde o email é o identificador único
    para autenticação em vez de nomes de utilizador.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Cria e guarda um utilizador com o email e palavra-passe fornecidos.
        """
        if not email:
            raise ValueError('O Email deve ser definido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Cria e guarda um super-utilizador com o email e palavra-passe fornecidos.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O super-utilizador deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O super-utilizador deve ter is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


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


class AuthenticationUser(AbstractUser):
    # O username padrão não é mais necessário
    username = None
    email = models.EmailField(unique=True)
    
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
    cpf = EncryptedCharField(
        max_length=255,
        validators=[RegexValidator(r'^\d{11}$', 'CPF deve ter 11 dígitos numéricos.')]
    )
    # HMAC do CPF: garante unicidade e permite buscar sem guardar o CPF em texto.
    cpf_hash = models.CharField(max_length=64, unique=True, editable=False, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Define o campo de login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cpf']

    # ASSOCIE O NOVO GESTOR
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf_hash = hash_cpf(self.cpf)
        super().save(*args, **kwargs)

    def get_user_type(self):
        if hasattr(self, 'employee'):
            return 'employee'
        elif hasattr(self, 'parent'):
            return 'parent'
        return 'authentication_user'

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nome da Role")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
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
        AuthenticationUser,
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
        return f"{self.user.email} - {self.role.name if self.role else 'Sem função'}"