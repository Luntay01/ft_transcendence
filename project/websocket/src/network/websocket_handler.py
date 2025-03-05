import json
from urllib.parse import urlparse, parse_qs

from ..network.room_manager import register_player, unregister_player, connected_players
from ..network.redis_utils import broadcast_to_room, notify_players
from ..config import logger, MAX_PLAYERS_PER_ROOM
from ..game.game_manager import game_manager

"""		Handles a new WebSocket connection.
- Extracts player and room details from the connection URL.
- Registers the player if they are not already in the room.
- Listens for incoming messages and processes them.
- Handles player disconnection cleanup.
Args:
	websocket (WebSocketServerProtocol): The WebSocket connection.
	path (str): The request path containing query parameters.
"""
async def handler(websocket, path):
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

"""		Processes an incoming event from a WebSocket message.
- Handles player reconnection.
- Updates player positions.
- Broadcasts unhandled events to the entire room.
Args:
	data (dict): The parsed WebSocket message data.
	websocket (WebSocketServerProtocol): The sender WebSocket connection.
"""
async def process_incoming_event(data, websocket):
	event = data.get("event")
	room_id = data.get("room_id")
	player_id = data.get("player_id")
	if event == "reconnect":
		logger.info(f"Player {player_id} has reconnected to Room {room_id}")
		await notify_players(room_id, {"event": "player_reconnected", "room_id": room_id, "player_id": player_id})
	elif event == "player_position":
		position = data.get("position")
		room_id = str(room_id)
		game_instance = game_manager.games.get(room_id)
		if not game_instance:
			logger.error(f"Game instance for Room {room_id} not found. Cannot update player position.")
			return
		game_instance.update_player_position(player_id, position)
	else:
		await broadcast_to_room(room_id, data, exclude=websocket)
