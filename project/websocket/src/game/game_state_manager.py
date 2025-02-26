import json
from ..config import redis_client, logger

""" ✅ Manages saving and retrieving game state from Redis. """
class GameStateManager:
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

	def save_game_state(self, room_id, game_data):
		redis_client.set(f"room_state:{room_id}", json.dumps(game_data))
		logger.info(f"Game state saved for Room {room_id}.")

	def load_game_state(self, room_id):
		data = redis_client.get(f"room_state:{room_id}")
		if data:
			logger.info(f"Loaded game state for Room {room_id}.")
		return data

	def clear_game_state(self, room_id):
		redis_client.delete(f"room_state:{room_id}")
		logger.info(f"Redis game state cleared for Room {room_id}.")

game_state_manager = GameStateManager()
