from ..network.redis_utils import publish_to_redis
import time

""" Still deciding up how i would like to send ball updates or update """
""" could be replacing update intervals with ball set destinations """
class BallPublisher:
	def __init__(self, ball_manager):
		self.ball_manager = ball_manager
		self.last_update_time = 0
		self.update_interval = 0.03

	async def publish_all_ball_updates(self):
		current_time = time.time()
		if current_time - self.last_update_time < self.update_interval:
			return  # ⏳
		self.last_update_time = current_time
		updates = []
		for ball in self.ball_manager.balls:
			updates.append({
				"ball_id": ball.id,
				"position": {"x": ball.position.x, "y": ball.position.y, "z": ball.position.z},
				"velocity": {"x": ball.velocity.x, "y": ball.velocity.y, "z": ball.velocity.z}
			})
		if updates:
			await publish_to_redis("ball_updates", {
				"event": "ball_updates",
				"room_id": self.ball_manager.room_id,
				"balls": updates
			})

	async def publish_ball_update(self, ball):
		ball_update_event = {
			"event": "ball_update",
			"room_id": self.room_id,
			"ball_id": ball.id,
			"position": {"x": ball.position.x, "y": ball.position.y, "z": ball.position.z},
			"velocity": {"x": ball.velocity.x, "y": ball.velocity.y, "z": ball.velocity.z}
		}
		await publish_to_redis("ball_update", ball_update_event)

"""
class BallPublisher:
	def __init__(self, ball_manager):
		self.ball_manager = ball_manager
		self.room_id = ball_manager.room_id

	async def publish_ball_update(self, ball):
		ball_update_event = {
			"event": "ball_update",
			"room_id": self.room_id,
			"ball_id": ball.id,
			"position": {"x": ball.position.x, "y": ball.position.y, "z": ball.position.z},
			"velocity": {"x": ball.velocity.x, "y": ball.velocity.y, "z": ball.velocity.z}
		}
		await publish_to_redis("ball_update", ball_update_event)
"""