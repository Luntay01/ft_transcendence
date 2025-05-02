from ..config import logger, update_logger
from .game import Game
from .game_state_manager import game_state_manager

""" 
	Manages game creation, updates, and overall game state. 
	This class ensures all game sessions are properly managed and updated in real-time.
"""
class GameManager:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True
		self.games = {}

	def create_game(self, room_id, players, game_mode, match_type):
		room_id = str(room_id)
		if room_id not in self.games:
			self.games[room_id] = Game(room_id, players, self, game_mode, match_type)
			logger.info(f"Created game for Room {room_id}.")
			saved_state = game_state_manager.load_game_state(room_id)
			if saved_state and saved_state.get("is_active", False):
				logger.info(f"Restoring previous game state for Room {room_id}.")
				self.games[room_id].restore_state(saved_state)
		else:
			logger.warning(f"Game for Room {room_id} already exists.")

	def start_game(self, room_id):
		room_id = str(room_id)
		logger.info(f"Starting game for Room {room_id}...")
		game = self.games.get(room_id)
		if game:
			game.start()
			logger.info(f"Game started in Room {room_id}.")
		else:
			logger.error(f"No game found for Room {room_id} to start.")

	def update_games(self, delta_time):
		for game in self.games.values():
			if not game.is_active:
				continue
			game.update(delta_time)

	def cleanup_game(self, room_id):
		if room_id in self.games:
			self.games[room_id].ball_manager.stop()
			del self.games[room_id]
			logger.info(f"Game state for Room {room_id} removed.")
			game_state_manager.clear_game_state(room_id)

game_manager = GameManager()







"""
from ..config import logger, redis_client
from .game import Game
from ..network.room_manager import connected_players
import time

class GameManager:
	_instance = None
	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super(GameManager, cls).__new__(cls)
			cls._instance.__initialized = False
		return cls._instance
	
	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True
		self.games = {}
		self.room_cleanup_timers = {}
	
	def create_game(self, room_id, players):
		room_id = str(room_id)
		if room_id not in self.games:
			self.games[room_id] = Game(room_id, players)
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
		inactive_rooms = []
		current_time = time.time()
		for room_id, game in self.games.items():
			if not game.is_active and not hasattr(game, "countdown_finished"):
				logger.info(f"Skipping cleanup for Room {room_id} as countdown is still running.")
				continue
			if room_id not in connected_players or not connected_players[room_id]:
				if room_id not in self.room_cleanup_timers:
					self.room_cleanup_timers[room_id] = current_time
					logger.info(f"Room {room_id} marked for cleanup, waiting 30 seconds for possible reconnect.")
				elif current_time - self.room_cleanup_timers[room_id] > 30:
					logger.info(f"No players reconnected in Room {room_id}. Cleaning up.")
					inactive_rooms.append(room_id)
			elif game.is_active:
				if room_id in self.room_cleanup_timers:
					del self.room_cleanup_timers[room_id]
				game.update(delta_time)
		for room_id in inactive_rooms:
			self.cleanup_game(room_id)

	def cleanup_game(self, room_id):
		if room_id in self.games:
			self.games[room_id].ball_manager.stop()
			del self.games[room_id]
			logger.info(f"Game state for Room {room_id} removed.")
			redis_client.delete(f"room_state:{room_id}")
			logger.info(f"Redis data for Room {room_id} cleared.")
		if room_id in self.room_cleanup_timers:
			del self.room_cleanup_timers[room_id]
			logger.info(f"Cleanup timer for Room {room_id} removed.")

game_manager = GameManager()
"""