from django.db import models
from users.models import User
from .managers import RoomManager

class Room(models.Model):
	id			= models.AutoField(primary_key=True)
	#int_id		= models.IntegerField(default=-1)
	is_full		= models.BooleanField(default=False)
	players		= models.ManyToManyField(User, related_name='rooms')
	max_players	= models.IntegerField(default=4)
	game_type	= models.IntegerField(default=-1)
	matches_left= models.IntegerField(default=1)
	room_done	= models.BooleanField(default=False)
	created_at	= models.DateTimeField(auto_now_add=True)
	objects		= RoomManager()

	def __str__(self):		return f"Room {self.id}"
	def has_space(self):	return self.players.count() < self.max_players
	def add_player(self, player):
		if self.has_space():
			self.players.add(player)
			self._update_full_status()
	def update_game_type(self, game_type):
		if game_type is not None:
			self.game_type = game_type
			if self.game_type == 1:
				self.matches_left = 4
			self._update_full_status()
	def decrement_matches(self, matches):
		if matches:
			self.matches_left = matches
			self._update_full_status()
		if self.matches_left == 0:
			self.room_done = True
			self._update_full_status()
	def remove_player(self, player: User) -> None:
		if self.players.filter(id=player.id).exists():
			self.players.remove(player)
			self._update_full_status()
	def _update_full_status(self) -> None:
		if self.is_full and self.players.count() < self.max_players:
			self.is_full = False
		elif not self.is_full and self.players.count() == self.max_players:
			self.is_full = True
		self.save()
	def clear_room(self) -> None:
		self.players.clear()
		self.is_full = False
		self.game_type = -1
		self.matches_left = 1
		self.save()