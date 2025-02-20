from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from .managers import UserManager
# Create your models here.

# Users
# TODO: validate inputs
class User(AbstractBaseUser, PermissionsMixin):
	id = models.AutoField(auto_created=True, primary_key=True)
	email = models.EmailField(max_length=512, validators=[EmailValidator])
	PROVIDER = {
		'Pong': 'Pong',
		'42Oauth': '42Oauth',
	}
	provider = models.CharField(max_length=20, choices=PROVIDER, default='Pong')
	oauth_user_id = models.CharField(max_length=20, null=True)
	password = models.CharField(max_length=256)
	username = models.CharField(max_length=256, unique=True)
	picture = models.ImageField(upload_to='images/', default='images/default.png')

	otp_secret = models.CharField(max_length=256, null=True)
	is_verified = models.BooleanField(default=False)
	first_name = models.CharField(max_length=128)
	last_name = models.CharField(max_length=128)
	trophies = models.IntegerField(default=0)

	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	date_joined = models.DateTimeField(default=timezone.now)
	birth_day = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = 'id'
	REQUIRED_FIELDS = ['email', 'username']

	objects = UserManager()

	class Meta:
		unique_together = ('provider', 'email')

	def __str__(self):
		return f"{self.username} (Trophies: {self.trophies})"