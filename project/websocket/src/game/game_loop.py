import asyncio
from .game_manager import game_manager  # ✅ Use Singleton
from .room_cleanup import room_cleanup
from ..config import logger

"""
	Continuously updates all active games.
	Runs at a fixed interval (60 FPS).
"""
async def start_game_update_loop():
	while True:
		inactive_rooms = room_cleanup.check_inactive_rooms(game_manager)
		game_manager.update_games(delta_time=0.016)
		if inactive_rooms:
			for room_id in inactive_rooms:
				room_cleanup.cleanup_game(game_manager, room_id)
		await asyncio.sleep(0.016)
