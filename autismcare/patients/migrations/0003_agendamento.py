# Escrita à mão para o model Agendamento.
# Confirme com: python manage.py makemigrations --check --dry-run

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_initial'),
        ('users', '0002_alter_autenticationuser_managers_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agendamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_hora', models.DateTimeField(verbose_name='Data e Hora')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agendamentos', to='patients.child')),
                ('terapeuta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agendamentos', to='users.employee')),
            ],
            options={
                'verbose_name': 'Agendamento',
                'verbose_name_plural': 'Agendamentos',
                'ordering': ['data_hora'],
            },
        ),
    ]
