from django.db import models

# Create your models here.

# Users
# TODO: validate inputs
# TODO: password hashed
class User(models.Model):
	username = models.CharField(max_length=256, primary_key=True)
	password = models.CharField(max_length=256)
	email = models.EmailField(max_length=256, default="test@example.com")