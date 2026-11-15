# Criptografa o CPF e grava o hash para unicidade.
# Exige DJANGO_FIELD_ENCRYPTION_KEY definida. Não tem reversão.

import django.core.validators
from django.db import migrations, models

import users.fields
from users.fields import hash_cpf


def criptografar_cpfs(apps, schema_editor):
    AuthenticationUser = apps.get_model('users', 'AuthenticationUser')
    for user in AuthenticationUser.objects.all():
        user.cpf_hash = hash_cpf(user.cpf)
        user.save(update_fields=['cpf', 'cpf_hash'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_role_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='authenticationuser',
            name='cpf_hash',
            field=models.CharField(default='', editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name='authenticationuser',
            name='cpf',
            field=users.fields.EncryptedCharField(
                max_length=255,
                validators=[django.core.validators.RegexValidator(r'^\d{11}$', 'CPF deve ter 11 dígitos numéricos.')],
            ),
        ),
        migrations.RunPython(criptografar_cpfs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='authenticationuser',
            name='cpf_hash',
            field=models.CharField(default='', editable=False, max_length=64, unique=True),
        ),
    ]
