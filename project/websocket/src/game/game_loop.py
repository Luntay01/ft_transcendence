import asyncio
from .game_manager import game_manager
from .room_cleanup import room_cleanup
from ..config import logger
from ..network.redis_utils import publish_game_event

"""
	Continuously updates all active games.
	Runs at a fixed interval (60 FPS).
"""
async def start_game_update_loop():
	update_interval = 2.0
	last_update_time = 0.0
	while True:
		inactive_rooms = room_cleanup.check_inactive_rooms(game_manager)
		game_manager.update_games(delta_time=0.016)
		current_time = asyncio.get_event_loop().time()
		if current_time - last_update_time >= update_interval:
			last_update_time = current_time  # Reset timer
			await send_game_states_to_clients()
		if inactive_rooms:
			for room_id in inactive_rooms:
				room_cleanup.cleanup_game(game_manager, room_id)
		await asyncio.sleep(0.016)

"""
Sends the full game state for each active room to all connected clients.
"""
async def send_game_states_to_clients():
	for room_id, game in game_manager.games.items():
		game_state = {
			"event": "game_state",
			"room_id": room_id,
			"balls": [
				{
					"ball_id": ball.id,
					"position": {"x": ball.position.x, "y": ball.position.y, "z": ball.position.z},
					"velocity": {"x": ball.velocity.x, "y": ball.velocity.y, "z": ball.velocity.z},
				}
				for ball in game.ball_manager.balls
			],
			"players": [
				{"player_id": player_id, "position": game.player_positions[player_id], "lives": game.player_lives[player_id]}
				for player_id in game.player_positions
			],
			"eliminated_players": game.elimination_order
		}
		await publish_game_event("game_state", room_id, game_state)
		logger.info(f"Sent game state update for Room {room_id}")