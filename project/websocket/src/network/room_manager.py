from .state import connected_players
from .redis_utils import notify_players
from ..config import logger, MAX_PLAYERS_PER_ROOM, redis_client
import json

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
		logger.info(f"Player {player_id} is already connected in Room {room_id}. Updating WebSocket reference.")
		previous_state["websocket"] = websocket
	else:
		connected_players.setdefault(room_id, []).append({
			"websocket": websocket,
			"player_id": player_id,
			"username": username,
		})
		logger.info(f"Player {player_id} ({username}) joined room {room_id}.")
		await notify_players(room_id, {"event": "player_joined", "room_id": room_id, "player_id": player_id, "username": username})


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
			leave_event = {"event": "player_left", "room_id": room_id, "player_id": player_id}
			await notify_players(room_id, leave_event)