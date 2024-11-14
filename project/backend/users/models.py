from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password

# Create your models here.

# Users
# TODO: validate inputs
# TODO: password hashed
class User(models.Model):
	username = models.CharField(max_length=256, primary_key=True)
	password = models.CharField(max_length=256)
	email = models.EmailField(max_length=512, validators=[EmailValidator])

	def save(self, **kwargs):
		hashed = make_password(self.password)
		self.password = hashed
		super().save(**kwargs)