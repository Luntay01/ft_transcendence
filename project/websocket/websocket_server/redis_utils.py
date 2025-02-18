from .config import redis_client, logger
import json

"""
publish a message to a Redis channel
"""
async def publish_to_redis(channel, message):
	redis_client.publish(channel, json.dumps(message))
	#logger.info(f"Published to {channel}: {message}")

"""
send a message to all players in a room
"""
async def notify_players(room_id, message):
	from .room_manager import connected_players
	for player in connected_players.get(room_id, []):
		ws = player["websocket"]
		if ws.open:
			await ws.send(json.dumps(message))
			#logger.debug(f"Sent data to WebSocket: {message}")

"""
broadcast a message to all players in the room, excluding the sender
"""
async def broadcast_to_room(room_id, message, exclude=None):
	from .room_manager import connected_players
	for player in connected_players.get(room_id, []):
		ws = player["websocket"]
		if ws != exclude and ws.open:
			await ws.send(json.dumps(message))
