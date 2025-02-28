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
		gameMode = query_params.get("gameMode",[None])[0]

		if not room_id or not player_id or not username or not gameMode:
			raise ValueError("Missing room_id, player_id, username or gameMode")
		return room_id, player_id, username, gameMode
#grabs room for the room id passed, if exits it iterates through the dictionary to find the rooms existing game mode,
#if they match it returns the existing one and if not it returns null to tell the handler to setup a different room for that gamemode
	def get_gameMode(room_id):
   		room = connected_players.get(room_id, [])
    	if room:
        	for player in room:
            	gameMode = player.get("gameMode")
            	if gameMode:
            	    return gameMode
    	return None
	try:
		room_id, player_id, username, gameMode = parse_connection_params(path)
		existingGameMode = get_gameMode(room_id)
		if player_id in [p["player_id"] for p in connected_players.get(room_id, [])]:
			logger.info(f"Player {player_id} is reconnecting to Room {room_id}")
		#setup of new room if gamemodes dont match and not reconnecting to old match
		elif existingGameMode != gameMode:
			await register_player(websocket, room_id, player_id, username, gameMode)
		async for message in websocket:
			data = json.loads(message)
			data.update({"room_id": room_id, "player_id": player_id})
			await process_incoming_event(data, websocket)
	except ValueError as ve:
		logger.warning(f"Connection rejected: {ve}")
		await websocket.close()
	finally:
		await unregister_player(websocket, room_id, player_id, gameMode)


async def process_incoming_event(data, websocket):
	from .game_manager import GameManager
	game_manager = GameManager()
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
