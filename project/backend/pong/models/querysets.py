from django.db import models

class RoomQuerySet(models.QuerySet):
	def available(self):	return self.filter(is_full=False)
	def full(self):			return self.filter(is_full=True)
	def with_space(self):	return self.available().annotate(player_count=models.Count('players')).filter(player_count__lt=models.F('max_players'))