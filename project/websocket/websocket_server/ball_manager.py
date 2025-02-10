import asyncio
from .redis_utils import publish_to_redis
from .config import GAME_SETTINGS, logger

class BallManager:
	def __init__(self, room_id):
		self.room_id = room_id
		self.balls = []
		self.game_active = False
	
	def spawn_ball(self):
		asyncio.create_task(self._delayed_spawn())
	
	async def _delayed_spawn(self):
		await asyncio.sleep(1.5)
		ball_id = str(len(self.balls) + 1)
		initial_position = {"x": 0, "y": 0, "z": 0}
		initial_velocity = GAME_SETTINGS["ballPhysics"]["initialVelocity"]
		ball = {
			"id": ball_id,
			"position": initial_position,
			"velocity": initial_velocity,
			"last_position": initial_position.copy()
		}
		self.balls.append(ball)
		ball_spawn_event = {
			"event": "ball_spawn",
			"room_id": self.room_id,
			"ball_id": ball_id,
			"position": initial_position,
			"velocity": initial_velocity
		}
		await publish_to_redis("ball_spawn", ball_spawn_event)
		logger.info(f"Ball {ball_id} spawned in room {self.room_id}. Published to Redis.")
	
	def update_balls(self, delta_time):
		for ball in self.balls:
			self._update_ball_position(ball, delta_time)
			self._check_collisions(ball)
			asyncio.create_task(self._publish_ball_update(ball))
	
	def _update_ball_position(self, ball, delta_time):
		ball["position"]["x"] += ball["velocity"]["x"] * delta_time
		ball["position"]["z"] += ball["velocity"]["z"] * delta_time
	
	def _check_collisions(self, ball):
		bounds = GAME_SETTINGS["ballPhysics"]["bounds"]
		if not (bounds["minX"] <= ball["position"]["x"] <= bounds["maxX"]):
			ball["velocity"]["x"] *= -1
		if not (bounds["minZ"] <= ball["position"]["z"] <= bounds["maxZ"]):
			ball["velocity"]["z"] *= -1
	
	async def _publish_ball_update(self, ball):
		ball_update_event = {
			"event": "ball_update",
			"room_id": self.room_id,
			"ball_id": ball["id"],
			"position": ball["position"],
			"velocity": ball["velocity"]
		}
		await publish_to_redis("ball_update", ball_update_event)
		#logger.debug(f"Published to ball_update: {ball_update_event}")




"""
import random
import math
import asyncio
import json
from .config import GAME_SETTINGS, logger
from .room_manager import notify_players
from .redis_utils import publish_to_redis

class BallManager:
	def __init__(self, room_id):
		self.room_id = room_id
		self.balls = []  # List of active balls

	def spawn_ball(self):
		async def delayed_spawn():
			await asyncio.sleep(1.5)
			ball_id = len(self.balls) + 1
			initial_position = {"x": 0, "y": 0, "z": 0}  # Center of the field
			initial_velocity = GAME_SETTINGS["ballPhysics"]["initialVelocity"]

			ball = {
				"id": ball_id,
				"position": initial_position,
				"velocity": initial_velocity,
				"destination": None,
				"last_position": initial_position.copy()
			}
			self.balls.append(ball)

			# Correct Event Name: ball_spawn
			ball_spawn_event = {
				"event": "ball_spawn",
				"room_id": self.room_id,
				"ball_id": ball_id,
				"position": initial_position,
				"velocity": initial_velocity
			}
			await publish_to_redis("ball_spawn", ball_spawn_event)
			logger.info(f"Ball {ball_id} spawned in room {self.room_id}. Published to Redis.")

		asyncio.create_task(delayed_spawn())


	def update_balls(self, delta_time):
		#if not self.balls:
		#    logger.debug(f" No balls in room {self.room_id}.")
		#else:
		#    logger.debug(f" Updating {len(self.balls)} balls in room {self.room_id}.")

		for ball in self.balls:
			self._move_ball(ball, delta_time)
			asyncio.create_task(publish_to_redis("ball_update", {
				"event": "ball_update",
				"room_id": self.room_id,
				"ball_id": ball["id"],
				"position": ball["position"],
				"velocity": ball["velocity"]
			}))

	def _move_ball(self, ball, delta_time):
		bounds = GAME_SETTINGS["ballPhysics"]["bounds"]

		# Move the ball
		ball["position"]["x"] += ball["velocity"]["x"] * delta_time
		ball["position"]["z"] += ball["velocity"]["z"] * delta_time

		#logger.debug(f" Moving Ball {ball['id']} to X: {ball['position']['x']}, Z: {ball['position']['z']}")

		# Check for boundary collisions
		if ball["position"]["x"] <= bounds["minX"] or ball["position"]["x"] >= bounds["maxX"]:
			ball["velocity"]["x"] *= -1
			#logger.debug(f" Ball {ball['id']} bounced on X-axis")

		if ball["position"]["z"] <= bounds["minZ"] or ball["position"]["z"] >= bounds["maxZ"]:
			ball["velocity"]["z"] *= -1
			#logger.debug(f" Ball {ball['id']} bounced on Z-axis")









	def _broadcast_ball_update(self, ball):

		if self._has_significant_change(ball["last_position"], ball["position"]):
			ball["last_position"] = ball["position"].copy()
			asyncio.create_task(notify_players(self.room_id, {
				"event": "ball_update",
				"ball_id": ball["id"],
				"position": ball["position"],
				"velocity": ball["velocity"]
			}))

	def _reached_destination(self, ball):
		if not ball["destination"]:
			return True
		
		distance = math.sqrt(
			(ball["position"]["x"] - ball["destination"]["x"]) ** 2 +
			(ball["position"]["z"] - ball["destination"]["z"]) ** 2
		)
		return distance < 0.1

	def _has_significant_change(self, prev_pos, new_pos):

		threshold = 0.1
		dx = abs(prev_pos["x"] - new_pos["x"])
		dz = abs(prev_pos["z"] - new_pos["z"])
		return dx > threshold or dz > threshold

	def _handle_collisions(self, ball):

		# Check for collisions with paddles, garden beds, and other balls
		for other_ball in self.balls:
			if ball["id"] != other_ball["id"]:
				if self._check_ball_collision(ball, other_ball):
					self._resolve_ball_collision(ball, other_ball)

	def _check_ball_collision(self, ball1, ball2):

		radius = GAME_SETTINGS["collision"]["ballRadius"]
		dx = ball1["position"]["x"] - ball2["position"]["x"]
		dz = ball1["position"]["z"] - ball2["position"]["z"]
		distance = math.sqrt(dx**2 + dz**2)
		return distance < (2 * radius)  # If distance is less than sum of radii, they collide

	def _resolve_ball_collision(self, ball1, ball2):

		# Simple elastic collision response
		ball1["velocity"]["x"], ball2["velocity"]["x"] = ball2["velocity"]["x"], ball1["velocity"]["x"]
		ball1["velocity"]["z"], ball2["velocity"]["z"] = ball2["velocity"]["z"], ball1["velocity"]["z"]

		# Notify clients of the updated ball movement
		notify_players(self.room_id, {
			"event": "ball_update",
			"ball_id": ball1["id"],
			"velocity": ball1["velocity"]
		})
		notify_players(self.room_id, {
			"event": "ball_update",
			"ball_id": ball2["id"],
			"velocity": ball2["velocity"]
		})
		
"""


"""
	def _move_ball(self, ball, delta_time):
		bounds = GAME_SETTINGS["ballPhysics"]["bounds"]

		# Update position
		ball["position"]["x"] += ball["velocity"]["x"] * delta_time
		ball["position"]["z"] += ball["velocity"]["z"] * delta_time

		# Check X boundaries (left and right walls)
		if ball["position"]["x"] <= bounds["minX"] or ball["position"]["x"] >= bounds["maxX"]:
			ball["velocity"]["x"] *= -1  # Reverse X velocity
			ball["position"]["x"] = max(min(ball["position"]["x"], bounds["maxX"]), bounds["minX"])  # Keep inside bounds

		# Check Z boundaries (top and bottom walls)
		if ball["position"]["z"] <= bounds["minZ"] or ball["position"]["z"] >= bounds["maxZ"]:
			ball["velocity"]["z"] *= -1  # Reverse Z velocity
			ball["position"]["z"] = max(min(ball["position"]["z"], bounds["maxZ"]), bounds["minZ"])  # Keep inside bounds

		# Notify players only if movement is significant
		self._broadcast_ball_update(ball)
"""


"""
	def update_balls(self, delta_time):
		for ball in self.balls:
			prev_position = ball["position"].copy()
			self._move_ball(ball, delta_time)
			
			if self._has_significant_change(prev_position, ball["position"]):
				notify_players(self.room_id, {
					"event": "ball_update",
					"ball_id": ball["id"],
					"velocity": ball["velocity"],
					"destination": ball["destination"]
				})
"""


		
"""
	def spawn_ball(self):
		ball_id = len(self.balls) + 1
		initial_position = {"x": 0, "y": 0, "z": 0}  # Center of the field
		initial_velocity = GAME_SETTINGS["ballPhysics"]["initialVelocity"]

		ball = {
			"id": ball_id,
			"position": initial_position,
			"velocity": initial_velocity,
			"destination": None
		}
		self.balls.append(ball)

		# Notify all players in the room about the new ball
		asyncio.create_task(notify_players(self.room_id, {
			"event": "ball_spawn",
			"ball_id": ball_id,
			"position": initial_position,
			"velocity": initial_velocity
		}))
		"""