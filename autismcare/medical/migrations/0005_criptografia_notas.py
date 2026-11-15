# Criptografa as notas médicas (prontuário e anotações).
# Exige DJANGO_FIELD_ENCRYPTION_KEY definida. Não tem reversão.

from django.db import migrations

import users.fields


def recriptografar(apps, schema_editor):
    for nome, campo in (('MedicalHistory', 'description'), ('MedicalRecord', 'notes')):
        Model = apps.get_model('medical', nome)
        for obj in Model.objects.all():
            obj.save(update_fields=[campo])


class Migration(migrations.Migration):

    dependencies = [
        ('medical', '0004_registroacesso'),
        ('users', '0005_criptografia_cpf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalhistory',
            name='description',
            field=users.fields.EncryptedTextField(verbose_name='Descrição'),
        ),
        migrations.AlterField(
            model_name='medicalrecord',
            name='notes',
            field=users.fields.EncryptedTextField(blank=True, null=True, verbose_name='Anotações Médicas'),
        ),
        migrations.RunPython(recriptografar, migrations.RunPython.noop),
    ]
