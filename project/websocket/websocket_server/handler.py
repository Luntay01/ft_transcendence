from .room_manager import register_player, unregister_player
from .redis_utils import broadcast_to_room, notify_players
from .config import MAX_PLAYERS_PER_ROOM
from .logger import logger
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
		await register_player(websocket, room_id, player_id, username)
		async for message in websocket:
			data = json.loads(message)
			data.update({"room_id": room_id, "player_id": player_id})
			await broadcast_to_room(room_id, data, exclude=websocket)
	except ValueError as ve:
		logger.warning(f"Connection rejected: {ve}")
		await websocket.close()
	finally:
		await unregister_player(websocket, room_id, player_id)
