from django.db import models
from users.models import User
from .managers import RoomManager

class Room(models.Model):
	id			= models.AutoField(primary_key=True)
	is_full		= models.BooleanField(default=False)
	players		= models.ManyToManyField(User, related_name='rooms')
	max_players	= models.IntegerField(default=4)
	gameMode	= models.CharField(max_length=50, default='default')
	created_at	= models.DateTimeField(auto_now_add=True)
	objects		= RoomManager()

	def __str__(self):		return f"Room {self.id}"
	def has_space(self):	return self.players.count() < self.max_players
	def add_player(self, player):
		if self.has_space():
			self.players.add(player)
			self._update_full_status()
	def update_gameMode(self, game_mode):
		if not game_mode == null
			self.gameMode = game_mode
		self.save()	
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
		self.gameMode = 'default'
		self.save()