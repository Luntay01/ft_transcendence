import asyncio
import json
from ..config import redis_client, logger, REDIS_CHANNELS
from ..network.redis_utils import notify_players
from ..network.event_handler import handle_event

"""		Listens for game-related events from Redis and processes them.
- Subscribes to key Redis channels.
- Forwards messages to `handle_event` for processing.
- Notifies WebSocket-connected players with updates.
Example:
	asyncio.create_task(start_redis_listener())
 """
async def start_redis_listener():

	pubsub = redis_client.pubsub()
	pubsub.subscribe(*REDIS_CHANNELS["game_events"])
	logger.info(f"Subscribed to Redis channels:{', '.join(REDIS_CHANNELS['game_events'])}")
	while True:
		message = pubsub.get_message(ignore_subscribe_messages=True)
		if message and message["type"] == "message":
			data = json.loads(message["data"])
			room_id = str(data.get("room_id"))
			event = data.get("event")
			await handle_event(event, room_id, data)
			await notify_players(room_id, data)
		await asyncio.sleep(0.016)  # prevent high CPU usage (approx. 60 FPS)
