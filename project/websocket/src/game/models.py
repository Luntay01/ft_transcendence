# src/game/models.py
from dataclasses import dataclass

@dataclass
class Vector:
	x: float
	y: float
	z: float

@dataclass
class Ball:
	id: str
	position: Vector
	velocity: Vector
	last_position: Vector
	last_collision_id: str = None