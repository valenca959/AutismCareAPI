from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from .base import AutenticationUser

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