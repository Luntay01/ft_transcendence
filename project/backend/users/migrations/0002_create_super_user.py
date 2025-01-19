import os
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    def generate_superuser(apps, schema_editor):
        from users.models import User

        DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        DJANGO_SUPERUSER_FIRST_NAME = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Kaladin')

        superuser = User.objects.create_superuser(
            username=DJANGO_SUPERUSER_USERNAME,
            email=DJANGO_SUPERUSER_EMAIL,
            password=DJANGO_SUPERUSER_PASSWORD,
            first_name=DJANGO_SUPERUSER_FIRST_NAME)

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]
