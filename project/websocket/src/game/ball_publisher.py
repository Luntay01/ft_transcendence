from ..network.redis_utils import publish_to_redis

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