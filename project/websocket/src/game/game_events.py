import asyncio
from ..network.redis_utils import publish_game_event
from ..config import logger

async def start_countdown(room_id):
	countdown_values = [3, 2, 1, "GO"]
	for count in countdown_values:
		await publish_game_event("start_game_countdown", room_id, {"countdown": count})
		logger.info(f"Room {room_id}: Countdown {count}")
		await asyncio.sleep(1)
