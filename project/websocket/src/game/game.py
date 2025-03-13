from .ball_manager import BallManager
from ..config import logger, GAME_SETTINGS
import asyncio
import copy
import aiohttp #TODO:Might be better to replace this and just publish to redis and then have the backend subscribed to the event
from datetime import datetime, timezone
#from ..network.redis_utils import publish_game_event
from .game_events import start_countdown
#from .player_manager import eliminate_player

class Game:
	def __init__(self, room_id, players, game_manager, game_mode):
		self.room_id = room_id
		self.players = players
		self.game_manager = game_manager
		self.is_active = False
		self.countdown_finished = False
		self.elapsed_time = 0
		self.last_spawn_interval = 0
		self.game_mode = game_mode
		self.player_positions = {}
		self.elimination_order = []
		self.start_time = datetime.utcnow() #TODO:need to chnage this to like self.start_time = datetime.now(timezone.utc) but has to sync with backend
		self.ball_manager = BallManager(self, room_id, self.player_positions)
		self.player_lives = {str(player["player_id"]): GAME_SETTINGS["scoring"]["startingScore"] for player in players}
		if self.game_mode == "2-player":
			self.goal_keys = ["bottom", "top"]
		else:
			self.goal_keys = list(GAME_SETTINGS["scoring"]["goalZones"].keys())
		self.goal_zones = self._assign_goal_zones_from_players()
		self.current_bounds = copy.deepcopy(GAME_SETTINGS["ballPhysics"]["bounds"])
		if self.game_mode == "2-player":
			self.current_bounds["minX"] = -10
			self.current_bounds["maxX"] = 10
		self.countdown_task = None

	def update_player_position(self, player_id, position):
		if position is None:
			logger.error(f"Error: Received None position for Player {player_id}!")
			return
		if player_id not in self.player_positions:
			self.player_positions[player_id] = {"x": position["x"], "z": position["z"], "velocity": {"x": 0, "z": 0}}
		last_position = self.player_positions[player_id]
		velocity_x = position["x"] - last_position["x"]
		velocity_z = position["z"] - last_position["z"]
		self.player_positions[player_id] = {
			"x": position["x"],
			"z": position["z"],
			"velocity": {"x": velocity_x, "z": velocity_z}
		}

	def start(self):
		self.is_active = True
		logger.info(f"Starting game for Room {self.room_id}")
		if self.countdown_task:
			self.countdown_task.cancel()
		self.countdown_task = asyncio.create_task(self._start_game_sequence())

	async def _start_game_sequence(self):
		await start_countdown(self.room_id)
		self.countdown_finished = True
		self.ball_manager.spawn_ball()

	def update(self, delta_time):
		# TODO: still needs a lot of work on this ball pool and sync with frontend, and maybe even update predections
		self.elapsed_time += delta_time
		current_interval = int(self.elapsed_time // 10)
		if current_interval > self.last_spawn_interval:
			self.last_spawn_interval = current_interval
			self.ball_manager.spawner.try_spawn_new_ball()
		self.ball_manager.update_balls(delta_time)

	async def _end_game(self, winner_id):
		logger.info(f"Game over. Winner: Player {winner_id}")
		winner_id = int(winner_id)
		elimination_order_int = [int(pid) for pid in self.elimination_order]
		rankings = {player_id: index + 1 for index, player_id in enumerate(reversed(elimination_order_int))}
		player_results = [
			{
				"player_id": int(player["player_id"]),
				"username": player["username"],
				"score": self.player_lives[str(player["player_id"])],
				"placement": rankings.get(int(player["player_id"]), None)
			}
			for player in self.players
		]
		match_data = {
			"room_id": int(self.room_id),
			"winner_id": winner_id,
			"players": player_results,
			"start_time": self.start_time.isoformat(),
			"elimination_order": elimination_order_int
		}
		async with aiohttp.ClientSession() as session:
			async with session.post("http://nginx/api/pong/match_results/", json=match_data) as response:
				response_text = await response.text()
				logger.info(f"Match results response: {response.status} - {response_text}")
		self.game_manager.cleanup_game(self.room_id)
		logger.info(f"Game state cleaned up for Room {self.room_id}.")

	def restore_state(self, state):
		self.is_active = state.get("is_active", False)
		self.countdown_finished = state.get("countdown_finished", False)
		self.elapsed_time = state.get("elapsed_time", 0)
		self.player_positions = copy.deepcopy(state.get("player_positions", {}))
		self.player_lives = copy.deepcopy(state.get("player_lives", {}))
		self.goal_zones = copy.deepcopy(state.get("goal_zones", self._assign_goal_zones()))
		self.current_bounds = copy.deepcopy(state.get("current_bounds", GAME_SETTINGS["ballPhysics"]["bounds"]))
		logger.info(f"Game state restored for Room {self.room_id}.")

	def _assign_goal_zones_from_players(self):
		assigned_zones = copy.deepcopy(GAME_SETTINGS["scoring"]["goalZones"])
		for player in self.players:
			player_id = str(player["player_id"])
			zone_key = player["goal_zone"]
			assigned_zones[zone_key]["playerId"] = player_id
		return assigned_zones








"""
from .ball_manager import BallManager
from ..config import logger, GAME_SETTINGS
import asyncio
from ..network.redis_utils import publish_to_redis



class Game:
	def __init__(self, room_id, players):
		self.room_id = room_id
		self.players = players
		self.is_active = False
		self.countdown_finished = False
		self.elapsed_time = 0
		self.last_spawn_interval = 0
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
		self.elapsed_time += delta_time

		# Check if we've passed a new 10-second interval
		current_interval = int(self.elapsed_time // 10)
		if current_interval > self.last_spawn_interval:
			self.last_spawn_interval = current_interval
			self.ball_manager._try_spawn_new_ball()
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

"""