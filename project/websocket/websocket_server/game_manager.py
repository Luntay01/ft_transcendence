from .config import logger
from .game import Game
import time

class GameManager:
	def __init__(self):
		self.games = {}  # {room_id: game instance}
		self.room_cleanup_timers = {}
	
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
		from .room_manager import connected_players
		inactive_rooms = []
		current_time = time.time()
		for room_id, game in self.games.items():
			if room_id not in connected_players or not connected_players[room_id]:
				if room_id not in self.room_cleanup_timers:
					self.room_cleanup_timers[room_id] = current_time
					logger.info(f"Room {room_id} marked for cleanup, waiting 10 seconds for possible reconnect.")
				elif current_time - self.room_cleanup_timers[room_id] > 10:
					logger.info(f"No players reconnected in Room {room_id}. Cleaning up.")
					inactive_rooms.append(room_id)
			elif game.is_active:
				if room_id in self.room_cleanup_timers:
					del self.room_cleanup_timers[room_id]
				game.update(delta_time)
		for room_id in inactive_rooms:
			self.cleanup_game(room_id)

	def cleanup_game(self, room_id):
		from .config import redis_client
		if room_id in self.games:
			del self.games[room_id]
			logger.info(f"Game state for Room {room_id} removed.")
			redis_client.delete(f"room_state:{room_id}")
			logger.info(f"Redis data for Room {room_id} cleared.")
		if room_id in self.room_cleanup_timers:
			del self.room_cleanup_timers[room_id]
			logger.info(f"Cleanup timer for Room {room_id} removed.")