from .ball_manager import BallManager
from .config import logger
import asyncio
from .redis_utils import publish_to_redis



class Game:
	def __init__(self, room_id, players):
		self.room_id = room_id
		self.players = players
		self.is_active = False
		self.ball_manager = BallManager(room_id)
		logger.debug(f"game initialized for room {room_id}")
	
	def start(self):
		self.is_active = True
		logger.info(f"starting game for Room {self.room_id}")
		asyncio.create_task(self._start_game_sequence())

	async def _start_game_sequence(self):
		await asyncio.sleep(2)
		await self._start_countdown()
		self.ball_manager.spawn_ball()
		# notify players the game has started not needed as django backend is already doing this
		#start_game_event = {
		#	"event": "start_game",
		#	"room_id": self.room_id,
		#	"players": [
		#		{"player_id": player["player_id"], "username": player["username"]}
		#		for player in self.players
		#	]
		#}

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
			await asyncio.sleep(2)  # 2-second interval between countdowns

	def update(self, delta_time):
		self.ball_manager.update_balls(delta_time)