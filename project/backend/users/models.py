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
	email = models.EmailField(max_length=512, validators=[EmailValidator], primary_key=True)
	password = models.CharField(max_length=256)
	username = models.CharField(max_length=256, unique=True)

	first_name = models.CharField(max_length=128)
	last_name = models.CharField(max_length=128)

	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	date_joined = models.DateTimeField(default=timezone.now)
	birth_day = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["username"]

	objects = UserManager()