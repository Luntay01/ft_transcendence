import asyncio
import random
from ..config import GAME_SETTINGS, logger
from ..network.redis_utils import publish_to_redis
from .models import Vector, Ball

class BallSpawner:
    def __init__(self, ball_manager):
        self.ball_manager = ball_manager
        self.room_id = ball_manager.room_id

    def spawn_ball(self):
        """Initiates the spawning of a new ball asynchronously."""
        asyncio.create_task(self._delayed_spawn())

    async def _delayed_spawn(self):
        """Handles the actual spawning after a delay."""
        await asyncio.sleep(GAME_SETTINGS["ballSpawn"]["delay"])
        spawn_positions = GAME_SETTINGS["ballSpawnPoints"]
        corner_name, spawn_point = random.choice(list(spawn_positions.items()))
        ball_id = str(len(self.ball_manager.balls) + 1)
        initial_position = Vector(x=spawn_point["x"], y=spawn_point["y"], z=spawn_point["z"])
        target_x = random.uniform(-1, 1)
        target_z = random.uniform(-1, 1)
        direction_x = target_x - spawn_point["x"]
        direction_z = target_z - spawn_point["z"]
        magnitude = (direction_x**2 + direction_z**2) ** 0.5
        velocity = Vector(
            x=(direction_x / magnitude) * GAME_SETTINGS["ballPhysics"]["initialVelocity"]["x"],
            y=-1.0,
            z=(direction_z / magnitude) * GAME_SETTINGS["ballPhysics"]["initialVelocity"]["z"]
        )
        ball = Ball(
            id=ball_id,
            position=initial_position,
            velocity=velocity,
            last_position=Vector(x=initial_position.x, y=initial_position.y, z=initial_position.z)
        )
        self.ball_manager.balls.append(ball)
        ball_spawn_event = {
            "event": "ball_spawn",
            "room_id": self.room_id,
            "ball_id": ball_id,
            "position": {"x": initial_position.x, "y": initial_position.y, "z": initial_position.z},
            "velocity": {"x": velocity.x, "y": velocity.y, "z": velocity.z}
        }
        await publish_to_redis("ball_spawn", ball_spawn_event)
        logger.info(f"🎾 Ball {ball_id} spawned from {corner_name} in room {self.room_id}.")

    def try_spawn_new_ball(self):
        """Checks if a new ball should be spawned based on game state."""
        active_players = sum(1 for lives in self.ball_manager.game.player_lives.values() if lives > 0)
        max_active_balls = GAME_SETTINGS["ballPhysics"]["maxBalls"]
        if len(self.ball_manager.balls) >= max_active_balls or active_players < 2:
            logger.info(f"🛑 No new ball spawned. Active Balls: {len(self.ball_manager.balls)}, Players Alive: {active_players}")
            return
        logger.info(f"⚡ Spawning new ball. Active Balls: {len(self.ball_manager.balls)}, Players Alive: {active_players}")
        self.spawn_ball()