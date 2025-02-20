from django.db import models

from authentication.models.base import AutenticationUser



class Parent(AutenticationUser):
    spouse = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} - {self.cpf}"

class Child(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="children")
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField(verbose_name="Data de Nascimento")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (Responsável: {self.parent.get_full_name()})"

class MedicalRecord(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name="registro_medico")
    allergies = models.TextField(verbose_name="Alergias", blank=True, null=True)
    notes = models.TextField(verbose_name="Anotações Médicas", blank=True, null=True)

    def __str__(self):
        return f"Prontuário de {self.child.first_name} {self.child.last_name}"

class MedicalHistory(models.Model):
    HISTORY_TYPES = [
        ("medication", "Medicação"),
        ("class", "Aula"),
        ("consultation", "Consulta"),
        ("other", "Outro"),
    ]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="historico_medico")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora do Registro")
    description = models.TextField(verbose_name="Descrição")
    history_type = models.CharField(max_length=20, choices=HISTORY_TYPES, default="other", verbose_name="Tipo de Registro")

    def __str__(self):
        return f"Evolução de {self.child.first_name} {self.child.last_name} em {self.date.strftime('%d/%m/%Y %H:%M')} - {self.get_history_type_display()}"

    class Meta:
        verbose_name = "Histórico Médico"
        verbose_name_plural = "Históricos Médicos"
        ordering = ["-date"]
