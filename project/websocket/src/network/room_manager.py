from .state import connected_players
from .redis_utils import notify_players
from ..config import logger, MAX_PLAYERS_PER_ROOM, redis_client
from ..game.game_manager import game_manager
import json
import asyncio

async def check_and_resume_game(room_id, rejoining_player_id=None):
	game = game_manager.games.get(room_id)
	if not game:
		logger.warning(f"No existing game found for Room {room_id}, cannot resume.")
		return
	if game.is_active:
		logger.info(f"Game in Room {room_id} is already active. No need to resume.")
		return
	await asyncio.sleep(0.5)
	connected_player_ids = {str(p["player_id"]) for p in connected_players.get(room_id, [])}
	expected_players = {str(p["player_id"]) for p in game.players}
	logger.info(f"Checking if all players are back: Expected {expected_players}, Connected {connected_player_ids}")
	if rejoining_player_id:
		for pending_player in list(game.pending_kicks.keys()):
			if rejoining_player_id not in game.pending_kicks[pending_player]:
				game.pending_kicks[pending_player].add(rejoining_player_id)
				logger.info(f"🗳 Auto-voting: Player {rejoining_player_id} votes to kick {pending_player} due to disconnection.")
	for player_id in list(game.pending_kicks.keys()):  
		if player_id in connected_player_ids:
			logger.info(f"Player {player_id} reconnected. Removing from pending kicks.")
			del game.pending_kicks[player_id]

	if expected_players.issubset(connected_player_ids):
		game.is_active = True
		logger.info(f"Game in Room {room_id} has been RESUMED after ALL players reconnected.")
		await notify_players(room_id, {"event": "game_resumed", "room_id": room_id})
	else:
		logger.info(f"Players still missing in Room {room_id}, game remains paused.")


"""		Registers a player in the specified room.
- Ensures the player has a username.
- Checks if the player is reconnecting or joining for the first time.
- Updates WebSocket reference if reconnecting.
- Notifies other players in the room about the new player.
Args:
	websocket (WebSocketServerProtocol): The player's WebSocket connection.
	room_id (str): The ID of the room.
	player_id (str): The player's unique identifier.
	username (str): The player's username.
"""
async def register_player(websocket, room_id, player_id, username):
	if not username:
		logger.warning(f"Player {player_id} has no username. Rejecting connection.")
		await websocket.close()
		return

	already_connected = False
	previous_state = None

	if room_id in connected_players:
		for player in connected_players[room_id]:
			if player["player_id"] == player_id:
				previous_state = player
				already_connected = True
				break
	if already_connected:
		logger.info(f"Player {player_id} is RECONNECTING to Room {room_id}. Updating WebSocket reference.")
		previous_state["websocket"] = websocket
	else:
		connected_players.setdefault(room_id, []).append({
			"websocket": websocket,
			"player_id": player_id,
			"username": username,
		})
		logger.info(f"Player {player_id} ({username}) JOINED Room {room_id}.")
		await notify_players(room_id, {
			"event": "player_joined", 
			"room_id": room_id, 
			"player_id": player_id, 
			"username": username
		})
	game = game_manager.games.get(room_id)
	if game and player_id in game.pending_kicks:
		logger.info(f"Player {player_id} reconnected. Removing from pending kicks.")
		del game.pending_kicks[player_id]
	await check_and_resume_game(room_id, rejoining_player_id=player_id)


"""		Unregisters a player when they disconnect.
- Removes the player from the room if they have disconnected.
- Stores their last known state in Redis for potential reconnection.
- Notifies other players that they have left.
Args:
	websocket (WebSocketServerProtocol): The player's WebSocket connection.
	room_id (str): The ID of the room.
	player_id (str): The player's unique identifier.
"""
async def unregister_player(websocket, room_id, player_id):
	if room_id in connected_players:
		player_to_remove = None
		for player in connected_players[room_id]:
			if player["player_id"] == player_id:
				if player["websocket"].open:
					logger.warning(f"Player {player_id} WebSocket is still open. Not removing.")
					return
				player_to_remove = player
				break
		if player_to_remove:
			connected_players[room_id].remove(player_to_remove)
			logger.info(f"Player {player_id} left room {room_id}.")
			player_state = {
				"player_id": player_id,
				"room_id": room_id,
				"username": player_to_remove["username"]
			}
			redis_client.set(f"player_state:{player_id}", json.dumps(player_state))
			leave_event = {
				"event": "player_left", 
				"room_id": room_id, 
				"player_id": player_id, 
				"username": player_to_remove["username"]
			}
			await notify_players(room_id, leave_event)
			game = game_manager.games.get(room_id)
			if game:
				logger.info(f"Player {player_id} is now pending kick in Room {room_id}.")
				game.pending_kicks[player_id] = set()
				game.is_active = False
				logger.info(f"Game in Room {room_id} is now PAUSED due to player disconnection.")
				await notify_players(room_id, {"event": "game_paused", "room_id": room_id})