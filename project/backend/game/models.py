from django.db import models
from django.utils import timezone

from users.models import User

class Game(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True)
	player = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	score = models.IntegerField()
	match_start = models.DateTimeField(default=timezone.now)
	match_end = models.DateTimeField(default=timezone.now)
	
