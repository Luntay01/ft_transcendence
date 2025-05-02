from ..game.game_manager import GameManager
from ..network.room_manager import connected_players
from ..config import logger
import asyncio

game_manager = GameManager()

"""
	Processes a game event received from Redis.

	Args:
		event (str): The event type (e.g., "start_game").
		room_id (str): The room identifier.
		data (dict): The event data payload.
"""
async def handle_event(event: str, room_id: str, data: dict):
	if event == "start_game":
		game_mode = data.get("gameMode", "4-player")
		match_type = data.get("matchType", "ranked")
		await ensure_all_players_connected(room_id, data["players"])
		#players = connected_players.get(room_id, [])
		players = data["players"]
		game_manager.create_game(room_id, players, game_mode, match_type)
		game_manager.start_game(room_id)
		logger.info(f"Game started for Room {room_id}")

"""
	Wait until all expected players are connected to the specified room.

	Args:
		room_id (str): The room identifier.
		expected_players_data (list): List of player data dictionaries expected in the room.
"""
async def ensure_all_players_connected(room_id: str, expected_players_data: list):
	expected_player_ids = {str(player["player_id"]) for player in expected_players_data}
	logger.info(f"Waiting for players {expected_player_ids} to connect to Room {room_id}...")
	while True:
		connected_player_ids = {player["player_id"] for player in connected_players.get(room_id, [])}
		if expected_player_ids.issubset(connected_player_ids):
			logger.info(f"All players connected to Room {room_id}: {connected_player_ids}")
			break
		await asyncio.sleep(0.1)
