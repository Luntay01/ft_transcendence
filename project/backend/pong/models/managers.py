from django.db import models
from .querysets import RoomQuerySet

class RoomManager(models.Manager):
	def get_queryset(self):						return RoomQuerySet(self.model, using=self._db)
	def available_rooms(self, max_players=4):	return self.get_queryset().available().with_space().filter(max_players=max_players)
	def full_rooms(self):						return self.get_queryset().full()
	def rooms_with_space(self):					return self.get_queryset().with_space()
	def create_room(self, max_players=4):		return self.create(max_players=max_players)