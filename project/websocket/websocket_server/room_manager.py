from .redis_utils import publish_to_redis, notify_players
from .logger import logger
from .config import MAX_PLAYERS_PER_ROOM

connected_players = {}  # {room_id: [websocket1, websocket2, ...]}

"""
register a player in the specified room
"""
async def register_player(websocket, room_id, player_id, username):
	if not username:
		logger.warning(f"Player {player_id} has no username. Rejecting connection.")
		await websocket.close()
		return
	connected_players.setdefault(room_id, []).append({ "websocket": websocket, "player_id": player_id, "username": username, })
	logger.info(f"Player {player_id} ({username}) joined room {room_id}.")
	await notify_players(room_id, {"event": "player_joined", "room_id": room_id, "player_id": player_id, "username": username,})
	if len(connected_players[room_id]) == MAX_PLAYERS_PER_ROOM:
		await start_game(room_id)

"""
unregister a player and clean up the room if empty
"""
async def unregister_player(websocket, room_id, player_id):
	if room_id in connected_players:
		connected_players[room_id] = [
			player for player in connected_players[room_id]
			if player["websocket"] != websocket
		]
		if not connected_players[room_id]:
			del connected_players[room_id]
	leave_event = {"event": "player_left", "room_id": room_id, "player_id": player_id}
	await notify_players(room_id, leave_event)
	logger.info(f"Player {player_id} left room {room_id}.")

"""
start a game when the room is full
"""
async def start_game(room_id):
	#players = [f"Player{index + 1}" for index in range(MAX_PLAYERS_PER_ROOM)]
	player_details = [
		{"player_id": player["player_id"], "username": player["username"]}
		for player in connected_players.get(room_id, [])
	]
	start_game_event = {
		"event": "start_game",
		"room_id": room_id,
		"players": player_details,
	}
	await publish_to_redis("start_game", start_game_event)
	await notify_players(room_id, start_game_event)
	logger.info(f"Room {room_id} is now full. Game started.")
