from django.db import models
from .child import Child
from .base import AutenticationUser

class Allergy(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MedicalRecord(models.Model):
    child = models.OneToOneField(
        Child,
        on_delete=models.CASCADE,
        related_name="registro_medico"
    )
    allergies = models.ManyToManyField(Allergy, blank=True, verbose_name="Alergias")
    notes = models.TextField(verbose_name="Anotações Médicas", blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prontuário de {self.child.first_name} {self.child.last_name}"

class MedicalHistory(models.Model):
    class HistoryType(models.TextChoices):
        MEDICATION = "medication", "Medicação"
        CLASS = "class", "Aula"
        CONSULTATION = "consultation", "Consulta"
        OTHER = "other", "Outro"

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="historico_medico"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora do Registro")
    description = models.TextField(verbose_name="Descrição")
    history_type = models.CharField(
        max_length=20,
        choices=HistoryType.choices,
        default=HistoryType.OTHER,
        verbose_name="Tipo de Registro"
    )
    created_by = models.ForeignKey(
        AutenticationUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evolução de {self.child.first_name} {self.child.last_name} em {self.date.strftime('%d/%m/%Y %H:%M')} - {self.get_history_type_display()}"

    class Meta:
        verbose_name = "Histórico Médico"
        verbose_name_plural = "Históricos Médicos"
        ordering = ["-date"]