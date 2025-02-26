from ..network.redis_utils import publish_game_event
from ..config import logger
import asyncio
from ..network.redis_utils import publish_to_redis
"""
async def eliminate_player(game, player_id):
	for zone_name, zone in game.goal_zones.items():
		if zone["playerId"] == player_id:
			zone["playerId"] = None
			logger.info(f"Removed Player {player_id}'s goal zone.")

			boundary_map = {
				"bottom": "maxZ",
				"top": "minZ",
				"left": "minX",
				"right": "maxX"
			}
			if zone_name in boundary_map:
				game.current_bounds[boundary_map[zone_name]] = 10 if "max" in boundary_map[zone_name] else -10
			logger.info(f"Bounds AFTER update: {game.current_bounds}")
			break

	await publish_game_event("player_eliminated", game.room_id, {"player_id": player_id})
	game.player_positions.pop(player_id, None)
"""
#need to check
async def eliminate_player(self, player_id):
	for zone_name, zone in self.goal_zones.items():
		if zone["playerId"] == player_id:
			zone["playerId"] = None  
			logger.info(f"🚫 Removed Player {player_id}'s goal zone.")
			if zone_name == "bottom":
				self.current_bounds["maxZ"] = 10
			elif zone_name == "top":
				self.current_bounds["minZ"] = -10
			elif zone_name == "left":
				self.current_bounds["minX"] = -10
			elif zone_name == "right":
				self.current_bounds["maxX"] = 10
			logger.info(f"📏 Bounds AFTER update: {self.current_bounds}")
			break
	elimination_event = {
		"event": "player_eliminated",
		"room_id": self.room_id,
		"player_id": player_id
	}
	await publish_to_redis("player_eliminated", elimination_event)
	if player_id in self.player_positions:
		del self.player_positions[player_id]
	remaining_players = [pid for pid, lives in self.player_lives.items() if lives > 0]
	if len(remaining_players) == 1:
		asyncio.create_task(self._end_game(winner_id=remaining_players[0]))
