from ..config import logger, redis_client
from ..network.room_manager import connected_players

"""Handles inactive room cleanup and player disconnections. """
class RoomCleanup:
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

	def check_inactive_rooms(self, game_manager):
		inactive_rooms = []
		for room_id, game in list(game_manager.games.items()):
			if self._should_cleanup_room(room_id):  
				inactive_rooms.append(room_id)
		return inactive_rooms

	def _should_cleanup_room(self, room_id):
		if room_id not in connected_players or not connected_players[room_id]:
			if not redis_client.exists(f"room_cleanup:{room_id}"):
				redis_client.set(f"room_cleanup:{room_id}", "inactive", ex=30)  
				logger.info(f"Room {room_id} marked for cleanup (30s countdown).")
				return False  
			logger.info(f"No players reconnected in Room {room_id}. Cleaning up...")
			return True
		return False

	def cleanup_game(self, game_manager, room_id):
		if room_id in game_manager.games:
			game_manager.games[room_id].ball_manager.stop()
			del game_manager.games[room_id]
			logger.info(f"Game state inroomcleanup.pyfor Room {room_id} removed.")
			redis_client.delete(f"room_state:{room_id}")
			redis_client.delete(f"room_cleanup:{room_id}")
			logger.info(f"Redis data for Room {room_id} cleared.")

room_cleanup = RoomCleanup()