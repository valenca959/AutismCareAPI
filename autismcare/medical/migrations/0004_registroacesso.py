# Escrita à mão para o model RegistroAcesso.
# Confirme com: python manage.py makemigrations --check --dry-run

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical', '0003_initial'),
        ('users', '0003_rename_autenticationuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroAcesso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recurso', models.CharField(max_length=50)),
                ('registro_id', models.CharField(blank=True, max_length=20)),
                ('acao', models.CharField(max_length=20)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='acessos_medicos', to='users.authenticationuser')),
            ],
            options={
                'verbose_name': 'Registro de acesso',
                'verbose_name_plural': 'Registros de acesso',
                'ordering': ['-criado_em'],
            },
        ),
    ]
