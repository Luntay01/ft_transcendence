from .config import logger
from .game import Game

class GameManager:
	def __init__(self):
		self.games = {}  # {room_id: game instance}
	def create_game(self, room_id, players):
		if room_id not in self.games:
			self.games[room_id] = Game(room_id, players)
			logger.info(f"created new game for room {room_id}")
		else:
			logger.warning(f"game for room {room_id} already exists.")
	def start_game(self, room_id):
		logger.info(f"starting game for room {room_id}")
		game = self.games.get(room_id)
		if game:
			logger.info(f"game found for room {room_id}, initiating start sequence.")
			game.start()
		else:
			logger.error(f"no game found for room {room_id} to start.")
	def update_games(self, delta_time):
		for game in self.games.values():
			if game.is_active:
				game.update(delta_time)