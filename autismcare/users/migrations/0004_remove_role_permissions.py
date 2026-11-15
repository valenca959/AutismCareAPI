from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_autenticationuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='permissions',
        ),
    ]
