from .ball_manager import BallManager
from .config import logger, GAME_SETTINGS
import asyncio
from .redis_utils import publish_to_redis



class Game:
	def __init__(self, room_id, players):
		self.room_id = room_id
		self.players = players
		self.is_active = False
		self.countdown_finished = False
		self.player_positions = {}
		self.ball_manager = BallManager(self, room_id, self.player_positions)
		self.player_lives = {str(player["player_id"]): GAME_SETTINGS["scoring"]["startingScore"] for player in players}
		self.goal_zones = GAME_SETTINGS["scoring"]["goalZones"]
		self.current_bounds = GAME_SETTINGS["ballPhysics"]["bounds"]

	def update_player_position(self, player_id, position):
		if position is None:
			logger.error(f"Error: Received None position for Player {player_id}!")
			return
		last_position = self.player_positions.get(player_id, position)
		velocity_x = position["x"] - last_position["x"]
		velocity_z = position["z"] - last_position["z"]
		self.player_positions[player_id] = {
			"x": position["x"],
			"z": position["z"],
			"velocity": {"x": velocity_x, "z": velocity_z}
		}

	def start(self):
		self.is_active = True
		logger.info(f"starting game for Room {self.room_id}")
		asyncio.create_task(self._start_game_sequence())

	async def _start_game_sequence(self):
		await self._start_countdown()
		self.countdown_finished = True
		self._assign_goal_zones()
		self.ball_manager.spawn_ball()

	def _assign_goal_zones(self):
		goal_keys = list(self.goal_zones.keys())
		for idx, player in enumerate(self.players):
			if idx < len(goal_keys):
				self.goal_zones[goal_keys[idx]]["playerId"] = str(player["player_id"])

	async def _start_countdown(self):
		countdown_values = [3, 2, 1, "GO"]
		for count in countdown_values:
			countdown_event = {
				"event": "start_game_countdown",
				"room_id": self.room_id,
				"countdown": count
			}
			await publish_to_redis("start_game_countdown", countdown_event)
			logger.info(f"Room {self.room_id}: Countdown {count}")
			await asyncio.sleep(1)  # 1 second interval between countdowns

	def update(self, delta_time):
		self.ball_manager.update_balls(delta_time)

	async def _eliminate_player(self, player_id):
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

	async def _end_game(self, winner_id):
		logger.info(f"game over Winner: Player {winner_id}")
		end_game_event = {
			"event": "game_over",
			"room_id": self.room_id,
			"winner_id": winner_id
		}
		await publish_to_redis("game_over", end_game_event)
		self.is_active = False
		self.countdown_finished = False
		self.player_lives.clear()
		self.goal_zones.clear()
		self.ball_manager.balls.clear()
