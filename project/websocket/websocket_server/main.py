import asyncio
import websockets
import json
from .handler import handler
from .redis_utils import redis_client, notify_players
from .logger import logger

"""
listen to Redis channels and relay messages to players
"""
async def redis_listener():
	pubsub = redis_client.pubsub()
	pubsub.subscribe("start_game", "update_position")
	try:
		while True:
			message = pubsub.get_message(ignore_subscribe_messages=True)
			if message and message["type"] == "message":
				data = json.loads(message["data"])
				room_id = data.get("room_id")
				if room_id:
					await notify_players(room_id, data)
			await asyncio.sleep(0.1)  # Prevent high CPU usage
	except Exception as e:
		logger.error(f"Redis listener error: {e}")


"""
main entry point to start the WebSocket server and Redis listener
"""
async def main():
	logger.info("Starting WebSocket server on ws://0.0.0.0:8765...")
	await asyncio.gather(
		websockets.serve(handler, "0.0.0.0", 8765),
		redis_listener(),
	)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except Exception as e:
		logger.error(f"Critical server error: {e}")


