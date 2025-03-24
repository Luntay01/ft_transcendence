from .ball_spawner import BallSpawner
from .ball_physics import BallPhysics
from .ball_collision_handler import CollisionHandler
from .ball_publisher import BallPublisher
from ..config import logger
import asyncio

class BallManager:
	def __init__(self, game, room_id, player_positions):
		self.game = game
		self.room_id = room_id
		self.balls = []
		self.update_task = None
		self.inactive_balls = []
		self.player_positions = player_positions 
		self.game_active = False
		self.spawner = BallSpawner(self)
		self.physics = BallPhysics()
		self.collisions = CollisionHandler(self)
		self.publisher = BallPublisher(self)

	def spawn_ball(self):
		self.spawner.spawn_ball()

	def despawn_ball(self, ball):
		if ball in self.balls:
			self.balls.remove(ball)
			self.inactive_balls.append(ball)
		self.spawner.try_spawn_new_ball()

	def update_balls(self, delta_time):
		if not self.game.is_active:
			return
		for ball in self.balls[:]:
			self.physics.update_ball_position(ball, delta_time)
			self.collisions.check_collisions(ball)
			#asyncio.create_task(self.publisher.publish_ball_update(ball))
			asyncio.create_task(self.publisher.publish_all_ball_updates())
	
	async def periodic_ball_updates(self):
		while self.game_active:
			for ball in self.balls[:]:
				self.physics.update_ball_position(ball, 0.016)
				self.collisions.check_collisions(ball)
			await self.publisher.publish_all_ball_updates()
			await asyncio.sleep(self.publisher.update_interval)

	def start(self):
		self.game_active = True
		if not hasattr(self, 'update_task') or not self.update_task:
			self.update_task = asyncio.create_task(self.periodic_ball_updates())

	def stop(self):
		self.game_active = False
		if hasattr(self, 'update_task') and self.update_task:
			self.update_task.cancel()
			self.update_task = None
		self.balls.clear()

