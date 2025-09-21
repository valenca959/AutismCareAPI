# autismcare/patients/models.py

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import AutenticationUser

class Parent(models.Model):
    user = models.OneToOneField(
        AutenticationUser,
        on_delete=models.CASCADE,
        related_name='parent'
    )
    spouse = models.CharField(max_length=100, blank=True, null=True)
    spouse_phone = PhoneNumberField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.cpf}"

    def get_children(self):
        return self.children.all()

    def save(self, *args, **kwargs):
        if hasattr(self.user, 'employee'):
            raise ValueError("Um usuário não pode ser tanto Parent quanto Employee.")
        super().save(*args, **kwargs)

class Child(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name="children"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField(verbose_name="Data de Nascimento")
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Responsável: {self.parent.user.get_full_name()})"

    class Meta:
        indexes = [models.Index(fields=['parent'])]