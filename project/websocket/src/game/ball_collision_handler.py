import math
import random
from ..config import GAME_SETTINGS, logger
from ..network.redis_utils import publish_to_redis
from .player_manager import eliminate_player
import asyncio

class CollisionHandler:
	def __init__(self, ball_manager):
		self.ball_manager = ball_manager
		self.game = ball_manager.game

	def check_collisions(self, ball):
		if ball.position.y > 0:
			return
		self._check_boundary_collisions(ball)
		self._check_player_collisions(ball)
		self._check_garden_bed_collisions(ball)
		self._check_goal_collisions(ball)
		self._check_ball_collisions(ball)

	def _check_ball_collisions(self, ball):
		balls = self.ball_manager.balls
		ball_radius = GAME_SETTINGS["collision"]["ballRadius"]
		total_radius_squared = (2 * ball_radius) ** 2 
		for other_ball in balls:
			if ball is other_ball:
				continue
			dx = other_ball.position.x - ball.position.x
			dz = other_ball.position.z - ball.position.z
			distance_squared = dx**2 + dz**2

			if distance_squared < total_radius_squared:
				self._resolve_ball_collision(ball, other_ball)

	def _resolve_ball_collision(self, ball1, ball2):
		dx = ball2.position.x - ball1.position.x
		dz = ball2.position.z - ball1.position.z
		distance = math.sqrt(dx**2 + dz**2)
		if distance == 0:
			return
		nx = dx / distance
		nz = dz / distance
		dvx = ball2.velocity.x - ball1.velocity.x
		dvz = ball2.velocity.z - ball1.velocity.z
		velocity_along_normal = dvx * nx + dvz * nz
		if velocity_along_normal > 0:
			return
		restitution = GAME_SETTINGS["collision"]["restitution"]
		impulse = (-(1 + restitution) * velocity_along_normal) / 2
		max_impulse = 5.0
		impulse = max(-max_impulse, min(impulse, max_impulse))
		ball1.velocity.x -= impulse * nx
		ball1.velocity.z -= impulse * nz
		ball2.velocity.x += impulse * nx
		ball2.velocity.z += impulse * nz
		overlap = (2 * GAME_SETTINGS["collision"]["ballRadius"]) - distance
		separation_bias = GAME_SETTINGS["collision"]["separationBias"]
		if overlap > 0:
			correction = (overlap + separation_bias) / 2
			ball1.position.x -= correction * nx
			ball1.position.z -= correction * nz
			ball2.position.x += correction * nx
			ball2.position.z += correction * nz
		min_speed = GAME_SETTINGS["ballPhysics"]["minBallSpeed"]
		for ball in (ball1, ball2):
			speed = math.sqrt(ball.velocity.x**2 + ball.velocity.z**2)
			if speed < min_speed:
				scale = min_speed / (speed + 1e-6)
				ball.velocity.x *= scale
				ball.velocity.z *= scale

	def _check_boundary_collisions(self, ball):
		bounds = self.game.current_bounds
		if not (bounds["minX"] <= ball.position.x <= bounds["maxX"]):
			ball.velocity.x *= -1
		if not (bounds["minZ"] <= ball.position.z <= bounds["maxZ"]):
			ball.velocity.z *= -1

	def _check_player_collisions(self, ball):
		if not self.ball_manager.player_positions:
			return
		ball_radius = GAME_SETTINGS["collision"]["ballRadius"]
		flower_pot_radius = GAME_SETTINGS["collision"]["flowerPotRadius"]
		total_radius_squared = (ball_radius + flower_pot_radius) ** 2
		for player_id, player in self.ball_manager.player_positions.items():
			if not player or "x" not in player or "z" not in player:
				continue
			distance_squared = (ball.position.x - player["x"]) ** 2 + (ball.position.z - player["z"]) ** 2
			if distance_squared <= total_radius_squared:
				ball.last_collision_id = player_id
				if distance_squared < (flower_pot_radius - ball_radius) ** 2:
					self._eject_ball_from_collider(ball, player)
				else:
					if ball.last_collision_id == player_id:
						continue
					self._handle_ball_deflection(ball, player)
			else:
				if ball.last_collision_id == player_id:
					ball.last_collision_id = None

	def _eject_ball_from_collider(self, ball, player_position):
		center_x, center_z = 0, 0
		to_center_x = center_x - ball.position.x
		to_center_z = center_z - ball.position.z
		to_center_length = math.sqrt(to_center_x ** 2 + to_center_z ** 2)
		if to_center_length == 0:
			to_center_x, to_center_z = 1, 0
		else:
			to_center_x /= to_center_length
			to_center_z /= to_center_length
		player_velocity = player_position.get("velocity", {"x": 0, "z": 0})
		player_speed = math.sqrt(player_velocity["x"] ** 2 + player_velocity["z"] ** 2)
		if player_speed > 0:
			move_dir_x = player_velocity["x"] / player_speed
			move_dir_z = player_velocity["z"] / player_speed
			influence_factor = GAME_SETTINGS["collision"]["influenceFactor"]
			blended_x = (to_center_x * (1 - influence_factor)) + (move_dir_x * influence_factor)
			blended_z = (to_center_z * (1 - influence_factor)) + (move_dir_z * influence_factor)
			blended_length = math.sqrt(blended_x ** 2 + blended_z ** 2)
			blended_x /= blended_length
			blended_z /= blended_length
		else:
			blended_x, blended_z = to_center_x, to_center_z
		original_speed = math.sqrt(ball.velocity.x ** 2 + ball.velocity.z ** 2)
		if original_speed < GAME_SETTINGS["collision"]["minimumSpeed"]:
			original_speed = GAME_SETTINGS["collision"]["minimumSpeed"]
		variance = random.uniform(-0.15, 0.15)
		final_x = blended_x * math.cos(variance) - blended_z * math.sin(variance)
		final_z = blended_x * math.sin(variance) + blended_z * math.cos(variance)
		ball.velocity.x = final_x * original_speed
		ball.velocity.z = final_z * original_speed

	def _check_garden_bed_collisions(self, ball):
		garden_bed_radius = GAME_SETTINGS["gardenBeds"]["radius"]
		for garden_bed in GAME_SETTINGS["gardenBeds"]["positions"]:
			distance_squared = (ball.position.x - garden_bed["x"]) ** 2 + (ball.position.z - garden_bed["z"]) ** 2
			if distance_squared <= garden_bed_radius ** 2:
				logger.warning(f"Ball collided with garden bed at {garden_bed['x']}, {garden_bed['z']}!")
				normal_x = ball.position.x - garden_bed["x"]
				normal_z = ball.position.z - garden_bed["z"]
				normal_length = math.sqrt(normal_x ** 2 + normal_z ** 2)
				if normal_length == 0:
					return
				normal_x /= normal_length
				normal_z /= normal_length
				dot_product = (ball.velocity.x * normal_x) + (ball.velocity.z * normal_z)
				ball.velocity.x -= 2 * dot_product * normal_x
				ball.velocity.z -= 2 * dot_product * normal_z

	def _check_goal_collisions(self, ball):
		if not self.game.countdown_finished:
			return
		for zone_name, zone in self.game.goal_zones.items():
			player_id = zone["playerId"]
			if not player_id:
				continue
			if (zone["minX"] <= ball.position.x <= zone["maxX"] and
				zone["minZ"] <= ball.position.z <= zone["maxZ"]):
				self.game.player_lives[player_id] -= 1
				logger.info(f"💀 Player {player_id} lost a life! Remaining: {self.game.player_lives[player_id]}")
				self.ball_manager.despawn_ball(ball)
				event_message = {
					"event": "ball_despawn",
					"room_id": self.game.room_id,
					"ball_id": ball.id,
					"player_id": player_id,
					"remaining_lives": self.game.player_lives[player_id]
				}
				asyncio.create_task(publish_to_redis("ball_despawn", event_message))
				if self.game.player_lives[player_id] <= 0:
					asyncio.create_task(eliminate_player(self.game, player_id))
				return

	def _handle_ball_deflection(self, ball, player):
		normal_x = ball.position.x - player["x"]
		normal_z = ball.position.z - player["z"]
		normal_length = math.sqrt(normal_x ** 2 + normal_z ** 2)
		if normal_length == 0:
			logger.warning(f"Collision normal is zero! Ball: {ball.position}, Player: {player}")
			return
		normal_x /= normal_length
		normal_z /= normal_length
		dot_product = (ball.velocity.x * normal_x) + (ball.velocity.z * normal_z)
		ball.velocity.x -= 2 * dot_product * normal_x
		ball.velocity.z -= 2 * dot_product * normal_z
		impact_speed = abs(dot_product)
		rebound_factor = GAME_SETTINGS["collision"]["reboundFactor"]
		damping_factor = GAME_SETTINGS["collision"]["dampingFactor"]
		ball.velocity.x *= rebound_factor if impact_speed > 1 else damping_factor
		ball.velocity.z *= rebound_factor if impact_speed > 1 else damping_factor
		speed = math.sqrt(ball.velocity.x ** 2 + ball.velocity.z ** 2)
		max_speed = GAME_SETTINGS["ballPhysics"]["maxSpeed"]
		min_speed = GAME_SETTINGS["collision"]["minimumSpeed"]
		if speed > max_speed:
			scale = max_speed / speed
			ball.velocity.x *= scale
			ball.velocity.z *= scale
		elif speed < min_speed:
			scale = min_speed / speed
			ball.velocity.x *= scale
			ball.velocity.z *= scale
		logger.info(f"Ball deflected. New Velocity: {ball.velocity}")