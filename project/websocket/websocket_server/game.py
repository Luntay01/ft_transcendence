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
		self.ball_manager = BallManager(room_id, self.player_positions)

	def update_player_position(self, player_id, position):
		if position is None:
			logger.error(f"Error: Received None position for Player {player_id}!")
			return
		last_position = self.player_positions.get(player_id, position)  # Get last known position
		velocity_x = position["x"] - last_position["x"]
		velocity_z = position["z"] - last_position["z"]
		self.player_positions[player_id] = {
			"x": position["x"],
			"z": position["z"],
			"velocity": {"x": velocity_x, "z": velocity_z}  # Store velocity
		}
		logger.info(f"Updated position for Player {player_id}: {position} (Velocity: {velocity_x}, {velocity_z})")

	def start(self):
		self.is_active = True
		logger.info(f"starting game for Room {self.room_id}")
		asyncio.create_task(self._start_game_sequence())

	async def _start_game_sequence(self):
		await self._start_countdown()
		self.countdown_finished = True
		self.ball_manager.spawn_ball()

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