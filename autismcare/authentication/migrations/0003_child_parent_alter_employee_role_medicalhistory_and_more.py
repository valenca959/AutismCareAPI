# Generated by Django 5.1.6 on 2025-02-20 00:42

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_autenticationuser_birthdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('birthdate', models.DateField(verbose_name='Data de Nascimento')),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('autenticationuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('spouse', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('authentication.autenticationuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='employee',
            name='role',
            field=models.CharField(choices=[('physiotherapist', 'Fisioterapeuta'), ('psychologist', 'Psicólogo'), ('pedagogue', 'Pedagogo'), ('assistant', 'Assistente'), ('receptionist', 'Recepcionista')], max_length=50),
        ),
        migrations.CreateModel(
            name='MedicalHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Data e Hora do Registro')),
                ('description', models.TextField(verbose_name='Descrição')),
                ('history_type', models.CharField(choices=[('medication', 'Medicação'), ('class', 'Aula'), ('consultation', 'Consulta'), ('other', 'Outro')], default='other', max_length=20, verbose_name='Tipo de Registro')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico_medico', to='authentication.child')),
            ],
            options={
                'verbose_name': 'Histórico Médico',
                'verbose_name_plural': 'Históricos Médicos',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allergies', models.TextField(blank=True, null=True, verbose_name='Alergias')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Anotações Médicas')),
                ('child', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='registro_medico', to='authentication.child')),
            ],
        ),
        migrations.AddField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='authentication.parent'),
        ),
    ]
