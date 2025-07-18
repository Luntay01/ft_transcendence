# Generated by Django 5.1.1 on 2025-03-03 03:31

import django.core.validators
import django.utils.timezone
from django.db import migrations, models
import pyotp

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=512, validators=[django.core.validators.EmailValidator])),
                ('provider', models.CharField(choices=[('Pong', 'Pong'), ('42Oauth', '42Oauth')], default='Pong', max_length=20)),
                ('oauth_user_id', models.CharField(max_length=20, null=True)),
                ('password', models.CharField(max_length=256)),
                ('username', models.CharField(max_length=256, unique=True)),
                ('picture', models.ImageField(default='images/default.png', upload_to='images/')),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('mfa', models.CharField(choices=[('Email', 'Email'), ('Authenticator', 'Authenticator')], max_length=20, default='Email')),
                ('trophies', models.IntegerField(default=0)),
                ('otp_secret', models.CharField(max_length=256, default=pyotp.random_base32)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('birth_day', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'unique_together': {('provider', 'email')},
            },
        ),
    ]
