# autismcare/medical/models.py

from django.db import models
from patients.models import Child
from users.models import AuthenticationUser
from users.fields import EncryptedTextField

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
    notes = EncryptedTextField(verbose_name="Anotações Médicas", blank=True, null=True)
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
    description = EncryptedTextField(verbose_name="Descrição")
    history_type = models.CharField(
        max_length=20,
        choices=HistoryType.choices,
        default=HistoryType.OTHER,
        verbose_name="Tipo de Registro"
    )
    created_by = models.ForeignKey(
        AuthenticationUser,
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

class RegistroAcesso(models.Model):
    """Registro de leitura de dados médicos (quem acessou, o quê e quando)."""
    usuario = models.ForeignKey(
        AuthenticationUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='acessos_medicos'
    )
    recurso = models.CharField(max_length=50)
    registro_id = models.CharField(max_length=20, blank=True)
    acao = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de acesso"
        verbose_name_plural = "Registros de acesso"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.usuario} {self.acao} {self.recurso} {self.registro_id} em {self.criado_em:%d/%m/%Y %H:%M}"
