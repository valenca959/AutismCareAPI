# Generated by Django 5.1.6 on 2025-02-17 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autenticationuser',
            name='birthdate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
