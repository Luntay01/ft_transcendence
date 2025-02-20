import asyncio
import math
import random
from .redis_utils import publish_to_redis
from .config import GAME_SETTINGS, logger

class BallManager:

	def __init__(self, game, room_id, player_positions):
		self.game = game
		self.room_id = room_id
		self.balls = []
		self.player_positions = player_positions
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
		ball["last_position"] = ball["position"].copy()
		ball["position"]["x"] += ball["velocity"]["x"] * delta_time
		ball["position"]["z"] += ball["velocity"]["z"] * delta_time
	
	def _check_collisions(self, ball):
		self._check_boundary_collisions(ball)
		self._check_player_collisions(ball)
		self._check_garden_bed_collisions(ball)
		self._check_goal_collisions(ball)
	
	def _check_goal_collisions(self, ball):
		if not self.game.countdown_finished:
			return
		for zone_name, zone in self.game.goal_zones.items():
			player_id = zone["playerId"]
			if not player_id:
				continue
			if (zone["minX"] <= ball["position"]["x"] <= zone["maxX"] and
				zone["minZ"] <= ball["position"]["z"] <= zone["maxZ"]):
				self.game.player_lives[player_id] -= 1
				logger.info(f"💀 Player {player_id} lost a life! Remaining: {self.game.player_lives[player_id]}")
				self.balls.remove(ball)
				event_message = {
					"event": "ball_despawn",
					"room_id": self.game.room_id,
					"ball_id": ball["id"],
					"player_id": player_id,
					"remaining_lives": self.game.player_lives[player_id]
				}
				asyncio.create_task(publish_to_redis("ball_despawn", event_message))
				if self.game.player_lives[player_id] <= 0:
					self.game._eliminate_player(player_id)
				return

	def _check_boundary_collisions(self, ball):
		bounds = GAME_SETTINGS["ballPhysics"]["bounds"]
		if not (bounds["minX"] <= ball["position"]["x"] <= bounds["maxX"]):
			ball["velocity"]["x"] *= -1
		if not (bounds["minZ"] <= ball["position"]["z"] <= bounds["maxZ"]):
			ball["velocity"]["z"] *= -1

	def _check_player_collisions(self, ball):
		if not self.player_positions:
			return
		logger.debug(f"🔎 Checking collision for Ball {ball['id']}. Total Players: {len(self.player_positions)}")
		ball_radius = GAME_SETTINGS["collision"]["ballRadius"]
		flower_pot_radius = GAME_SETTINGS["collision"]["flowerPotRadius"]
		total_radius_squared = (ball_radius + flower_pot_radius) ** 2  
		last_collision = ball.get("last_collision_id")
		for player_id, player in self.player_positions.items():
			if not player or "x" not in player or "z" not in player:
				continue
			player_position = player  
			distance_squared = (ball["position"]["x"] - player_position["x"]) ** 2 + \
							(ball["position"]["z"] - player_position["z"]) ** 2
			if distance_squared <= total_radius_squared:
				ball["last_collision_id"] = player_id  
				if distance_squared < (flower_pot_radius - ball_radius) ** 2:
					self._eject_ball_from_collider(ball, player_position)
				else:
					if last_collision == player_id:
						continue  
					self._handle_ball_deflection(ball, player)
			else:
				if last_collision == player_id:
					ball["last_collision_id"] = None
	
	def _eject_ball_from_collider(self, ball, player_position):
		center_x, center_z = 0, 0
		to_center_x = center_x - ball["position"]["x"]
		to_center_z = center_z - ball["position"]["z"]
		to_center_length = math.sqrt(to_center_x ** 2 + to_center_z ** 2)
		if to_center_length == 0:
			to_center_x, to_center_z = 1, 0
		to_center_x /= to_center_length
		to_center_z /= to_center_length
		player_velocity = player_position.get("velocity", {"x": 0, "z": 0})
		player_speed = math.sqrt(player_velocity["x"] ** 2 + player_velocity["z"] ** 2)
		if player_speed > 0:
			move_dir_x = player_velocity["x"] / player_speed
			move_dir_z = player_velocity["z"] / player_speed
			influence_factor = 0.5  # adjust this to control the balance
			blended_x = (to_center_x * (1 - influence_factor)) + (move_dir_x * influence_factor)
			blended_z = (to_center_z * (1 - influence_factor)) + (move_dir_z * influence_factor)
			blended_length = math.sqrt(blended_x ** 2 + blended_z ** 2)
			blended_x /= blended_length
			blended_z /= blended_length
		else:
			blended_x, blended_z = to_center_x, to_center_z
		original_speed = math.sqrt(ball["velocity"]["x"] ** 2 + ball["velocity"]["z"] ** 2)
		if original_speed < GAME_SETTINGS["collision"]["minimumSpeed"]:
			original_speed = GAME_SETTINGS["collision"]["minimumSpeed"]
		variance = random.uniform(-0.15, 0.15)  # small deviation
		final_x = blended_x * math.cos(variance) - blended_z * math.sin(variance)
		final_z = blended_x * math.sin(variance) + blended_z * math.cos(variance)
		ball["velocity"]["x"] = final_x * original_speed
		ball["velocity"]["z"] = final_z * original_speed

	def _check_garden_bed_collisions(self, ball):
		garden_bed_radius = GAME_SETTINGS["gardenBeds"]["radius"]
		for garden_bed in GAME_SETTINGS["gardenBeds"]["positions"]:
			distance_squared = (ball["position"]["x"] - garden_bed["x"]) ** 2 + \
							(ball["position"]["z"] - garden_bed["z"]) ** 2
			if distance_squared <= garden_bed_radius ** 2:
				logger.warning(f"Ball collided with garden bed at {garden_bed['x']}, {garden_bed['z']}!")
				normal_x = ball["position"]["x"] - garden_bed["x"]
				normal_z = ball["position"]["z"] - garden_bed["z"]
				normal_length = math.sqrt(normal_x ** 2 + normal_z ** 2)
				if normal_length == 0:
					return
				normal_x /= normal_length
				normal_z /= normal_length
				dot_product = (ball["velocity"]["x"] * normal_x) + (ball["velocity"]["z"] * normal_z)
				ball["velocity"]["x"] -= 2 * dot_product * normal_x
				ball["velocity"]["z"] -= 2 * dot_product * normal_z

	def _handle_ball_deflection(self, ball, player):
		ball_velocity = ball["velocity"]
		ball_position = ball["position"]
		player_position = player
		normal_x = ball_position["x"] - player_position["x"]
		normal_z = ball_position["z"] - player_position["z"]
		normal_length = math.sqrt(normal_x ** 2 + normal_z ** 2)
		if normal_length == 0:  
			logger.warning(f"Collision detected but normal vector is zero! Ball: {ball_position}, Player: {player_position}")
			return  # prevent / by zero
		normal_x /= normal_length
		normal_z /= normal_length
		normal = {"x": normal_x, "z": normal_z}
		dot_product = (ball_velocity["x"] * normal_x) + (ball_velocity["z"] * normal_z)
		ball_velocity["x"] -= 2 * dot_product * normal_x
		ball_velocity["z"] -= 2 * dot_product * normal_z
		impact_speed = abs(dot_product)  # how hard it hit the player
		rebound_factor = GAME_SETTINGS["collision"]["reboundFactor"]
		damping_factor = GAME_SETTINGS["collision"]["dampingFactor"]
		ball_velocity["x"] *= rebound_factor if impact_speed > 1 else damping_factor
		ball_velocity["z"] *= rebound_factor if impact_speed > 1 else damping_factor
		speed = math.sqrt(ball_velocity["x"] ** 2 + ball_velocity["z"] ** 2)
		max_speed = GAME_SETTINGS["ballPhysics"]["maxSpeed"]
		min_speed = GAME_SETTINGS["collision"]["minimumSpeed"]
		if speed > max_speed:
			scale = max_speed / speed
			ball_velocity["x"] *= scale
			ball_velocity["z"] *= scale
		elif speed < min_speed:
			scale = min_speed / speed
			ball_velocity["x"] *= scale
			ball_velocity["z"] *= scale
		logger.info(f"Ball deflected. New Velocity: {ball_velocity}")
	
	async def _publish_ball_update(self, ball):
		ball_update_event = {
			"event": "ball_update",
			"room_id": self.room_id,
			"ball_id": ball["id"],
			"position": ball["position"],
			"velocity": ball["velocity"]
		}
		await publish_to_redis("ball_update", ball_update_event)
	
	def stop(self):
		self.game_active = False
		self.balls.clear()
