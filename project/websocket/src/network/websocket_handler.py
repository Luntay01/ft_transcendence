import json
from urllib.parse import urlparse, parse_qs

from ..network.room_manager import register_player, unregister_player, connected_players
from ..network.redis_utils import broadcast_to_room, notify_players
from ..config import logger, MAX_PLAYERS_PER_ROOM
from ..game.game_manager import game_manager
from ..game.player_manager import eliminate_player

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
		game_type = query_params.get("game_type",[None])[0]

		game_type = int(game_type)
		if not (0 <= game_type < 4):
			raise ValueError("game_type out of range")

		logger.warning(f"gametype {game_type}")
		if not room_id or not player_id or not username:
			raise ValueError("Missssing room_id, player_id, username")
		return room_id, player_id, username, game_type
#grabs room for the room id passed, if exits it iterates through the dictionary to find the rooms existing game mode,
#if they match it returns the existing one and if not it returns null to tell the handler to setup a different room for that game_type
	def get_game_type(room_id):
		room = connected_players.get(room_id, [])
		if room:
			for player in room:
				game_type = player.get("game_type")
				if game_type:
					return game_type
		return None
	try:
		room_id, player_id, username, game_type = parse_connection_params(path)
		existing_game_type = get_game_type(room_id)
		if player_id in [p["player_id"] for p in connected_players.get(room_id, [])]:
			logger.info(f"Player {player_id} is reconnecting to Room {room_id}")
		#setup of new room if game_types dont match and not reconnecting to old match
		else:
			await register_player(websocket, room_id, player_id, username, game_type)
		async for message in websocket:
			data = json.loads(message)
			data.update({"room_id": room_id, "player_id": player_id})
			await process_incoming_event(data, websocket)
	except ValueError as ve:
		logger.warning(f"Connection rejected: {ve}")
		await websocket.close()
	finally:
		await unregister_player(websocket, room_id, player_id, game_type)

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
	if event == "vote_kick":
		vote_key = data.get("vote_key")
		if not vote_key or ":" not in vote_key:
			return
		voter_id, player_id = vote_key.split(":")
		logger.info(f"[process_incoming_event] Received vote: Room {room_id}, Voter {voter_id}, Target {player_id}")
		if voter_id == player_id:
			logger.error(f"ERROR: Player {voter_id} attempted to vote themselves out! This should not happen.")
			return
		await handle_vote_kick(room_id, player_id, voter_id)
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

async def handle_vote_kick(room_id, player_id, voter_id):
	room_id = str(room_id)
	logger.info(f"[handle_vote_kick] Received: Room {room_id}, Voter {voter_id}, Target {player_id}")
	if player_id == voter_id:
		logger.error(f"ERROR: Player {voter_id} is trying to vote themselves out! This should not happen.")
		return
	game = game_manager.games.get(room_id)
	if not game:
		logger.warning(f"Cannot vote kick in Room {room_id}, no active game found.")
		return
	if player_id not in game.pending_kicks:
		logger.warning(f"Player {player_id} is NOT in pending kicks. Ignoring vote.")
		return
	active_players = {p["player_id"] for p in connected_players.get(room_id, [])}
	logger.info(f"Player {voter_id} is voting to kick Player {player_id} in Room {room_id}.")
	logger.info(f"Active Players: {active_players}")
	if voter_id not in active_players:
		logger.warning(f"Invalid vote: Player {voter_id} is not in Room {room_id}.")
		return
	if voter_id in game.pending_kicks[player_id]:
		logger.info(f"Player {voter_id} already voted to kick Player {player_id}. Ignoring duplicate vote.")
		return
	game.pending_kicks[player_id].add(voter_id)
	total_votes_needed = len(active_players)
	logger.info(f"Player {player_id} has {len(game.pending_kicks[player_id])}/{total_votes_needed} votes to be kicked.")
	if len(game.pending_kicks[player_id]) >= total_votes_needed:
		logger.info(f"Player {player_id} has been voted out.")
		if player_id in game.player_lives:
			logger.info(f"Setting Player {player_id}'s lives to 0 for elimination.")
			game.player_lives[player_id] = 0
		await eliminate_player(game, player_id)
		await notify_players(room_id, {"event": "player_voted_out", "room_id": room_id, "player_id": player_id})
		del game.pending_kicks[player_id]
		if not game.pending_kicks:
			logger.info(f"All pending kicks resolved. Resuming game in Room {room_id}.")
			game.is_active = True
			await notify_players(room_id, {"event": "game_resumed", "room_id": room_id})
	else:
		logger.info(f"Waiting for more votes. {len(game.pending_kicks[player_id])}/{total_votes_needed} votes received.")

