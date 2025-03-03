from django.db import models
from users.models import User
from .room import Room
from django.utils.timezone import now

class MatchResult(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="matches")
	winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	players = models.ManyToManyField(User, related_name="match_results")
	elimination_order = models.JSONField(default=list)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField(auto_now_add=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Match {self.id} - Winner: {self.winner.username if self.winner else 'Unknown'}"
