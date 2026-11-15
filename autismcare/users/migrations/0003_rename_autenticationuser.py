# Renomeia AutenticationUser -> AuthenticationUser (tabela users_autenticationuser -> users_authenticationuser).
# Confirme com: python manage.py makemigrations --check --dry-run

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_autenticationuser_managers_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AutenticationUser',
            new_name='AuthenticationUser',
        ),
    ]
