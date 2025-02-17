from .room_manager import register_player, unregister_player, connected_players
from .redis_utils import broadcast_to_room, notify_players
from .config import logger, MAX_PLAYERS_PER_ROOM
import json

"""
handle WebSocket connections and manage player-room interactions
"""
async def handler(websocket, path):
	from urllib.parse import urlparse, parse_qs
	def parse_connection_params(path):
		parsed_path = urlparse(path)
		query_params = parse_qs(parsed_path.query)
		room_id = query_params.get("room_id", [None])[0]
		player_id = query_params.get("player_id", [None])[0]
		username = query_params.get("username", [None])[0]
		if not room_id or not player_id or not username:
			raise ValueError("Missing room_id, player_id, or username")
		return room_id, player_id, username
	try:
		room_id, player_id, username = parse_connection_params(path)
		# check if this player is reconnecting
		if player_id in [p["player_id"] for p in connected_players.get(room_id, [])]:
			logger.info(f"Player {player_id} is reconnecting to Room {room_id}")
		else:
			await register_player(websocket, room_id, player_id, username)
		async for message in websocket:
			data = json.loads(message)
			data.update({"room_id": room_id, "player_id": player_id})
			await process_incoming_event(data, websocket)
	except ValueError as ve:
		logger.warning(f"Connection rejected: {ve}")
		await websocket.close()
	finally:
		await unregister_player(websocket, room_id, player_id)


async def process_incoming_event(data, websocket):
	event = data.get("event")
	room_id = data.get("room_id")
	player_id = data.get("player_id")
	if event == "reconnect":
		logger.info(f"Player {player_id} has reconnected to Room {room_id}")
		await notify_players(room_id, {"event": "player_reconnected", "room_id": room_id, "player_id": player_id})
	elif event == "player_position":
		logger.info(f"Received position update from Player {player_id} in Room {room_id}")
		# store position data for collision handling (to be implemented)
	else:
		await broadcast_to_room(room_id, data, exclude=websocket)
