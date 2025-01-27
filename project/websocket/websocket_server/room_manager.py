from .redis_utils import publish_to_redis, notify_players
from .logger import logger
from .config import MAX_PLAYERS_PER_ROOM

connected_players = {}  # {room_id: [websocket1, websocket2, ...]}

"""
register a player in the specified room
"""
async def register_player(websocket, room_id, player_id):
	connected_players.setdefault(room_id, []).append(websocket)
	logger.info(f"Player {player_id} joined room {room_id}.")
	await notify_players(room_id, {"event": "player_joined", "room_id": room_id, "player_id": player_id})
	if len(connected_players[room_id]) == MAX_PLAYERS_PER_ROOM:
		await start_game(room_id)

"""
unregister a player and clean up the room if empty
"""
async def unregister_player(websocket, room_id, player_id):
	if room_id in connected_players:
		connected_players[room_id].remove(websocket)
		if not connected_players[room_id]:
			del connected_players[room_id]
	leave_event = {"event": "player_left", "room_id": room_id, "player_id": player_id}
	await notify_players(room_id, leave_event)
	logger.info(f"Player {player_id} left room {room_id}.")

"""
start a game when the room is full
"""
async def start_game(room_id):
	players = [f"Player{index + 1}" for index in range(MAX_PLAYERS_PER_ROOM)]
	start_game_event = {
		"event": "start_game",
		"room_id": room_id,
		"players": players,
	}
	await publish_to_redis("start_game", start_game_event)
	await notify_players(room_id, start_game_event)
	logger.info(f"Room {room_id} is now full. Game started.")
