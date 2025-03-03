#from ..network.redis_utils import publish_game_event
from ..config import logger
import asyncio
from ..network.redis_utils import publish_to_redis

async def eliminate_player(self, player_id):
	for zone_name, zone in self.goal_zones.items():
		if zone["playerId"] == player_id:
			zone["playerId"] = None  
			logger.info(f"Removed Player {player_id}'s goal zone.")
			if zone_name == "bottom":
				self.current_bounds["maxZ"] = 10
			elif zone_name == "top":
				self.current_bounds["minZ"] = -10
			elif zone_name == "left":
				self.current_bounds["minX"] = -10
			elif zone_name == "right":
				self.current_bounds["maxX"] = 10
			logger.info(f"Bounds AFTER update: {self.current_bounds}")
			break
	if player_id not in self.elimination_order:
		self.elimination_order.append(player_id)
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
		self.elimination_order.append(remaining_players[0])
		asyncio.create_task(self._end_game(winner_id=remaining_players[0]))
