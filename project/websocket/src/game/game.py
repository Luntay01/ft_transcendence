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
	def __init__(self, room_id, players, game_manager, game_mode, game_type):
		self.room_id = room_id
		self.players = players
		self.game_manager = game_manager
		self.is_active = False
		self.pending_kicks = {}
		self.countdown_finished = False
		self.elapsed_time = 0
		self.last_spawn_interval = 0
		self.game_mode = game_mode
		self.game_type = game_type
		self.room_done = False
		self.matches = 1
		self.signal = 0
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
			if self.is_active:
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
		#if self.game_type != 1:
		self.game_manager.cleanup_game(self.room_id)
		logger.info(f"Game state ingame.pycleaned up for Room {self.room_id}.")

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
