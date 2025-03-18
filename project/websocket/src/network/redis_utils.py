from ..config import redis_client, logger, update_logger
from .state import connected_players
import json

"""		Publishes a message to a Redis channel.
Args:
	channel (str): The Redis channel name.
	message (dict): The message payload.
Example:
	await publish_to_redis("game_events", {"event": "ball_spawn", "room_id": "1"})
"""
async def publish_to_redis(channel, message):
	redis_client.publish(channel, json.dumps(message))
	update_logger.debug(f"Published to Redis: {channel} -> {message}")


"""		Sends a message to all players in a given room.
Args:
	room_id (str): The room identifier.
	message (dict): The message payload.
Example:
	await notify_players("1", {"event": "player_joined", "player_id": "123"})
"""
async def notify_players(room_id, message):
	if room_id not in connected_players:
		logger.warning(f"Attempted to notify players in non-exsistent Room {room_id}.")
		return
	for player in connected_players.get(room_id, []):
		ws = player["websocket"]
		if ws.open:
			await ws.send(json.dumps(message))
			update_logger.debug(f"Sent data to WebSocket: {message}")


"""		Broadcasts a message to all players in the room, excluding a specified player.
Args:
	room_id (str): The room identifier.
	message (dict): The message payload.
	exclude (WebSocketServerProtocol, optional): The WebSocket to exclude from the broadcast.
Example:
	await broadcast_to_room("1", {"event": "player_scored", "score": 10}, exclude=some_websocket)
"""
async def broadcast_to_room(room_id, message, exclude=None):
	if room_id not in connected_players:
		logger.warning(f"Attempted to notify players in non-exsistent Room {room_id}.")
		return
	for player in connected_players.get(room_id, []):
		ws = player["websocket"]
		if ws != exclude and ws.open:
			await ws.send(json.dumps(message))

async def publish_game_event(event, room_id, payload):
	payload["event"] = event
	payload["room_id"] = room_id
	channel = event
	redis_client.publish(channel, json.dumps(payload))
	logger.debug(f"Published {event} -> {payload} on {channel}")