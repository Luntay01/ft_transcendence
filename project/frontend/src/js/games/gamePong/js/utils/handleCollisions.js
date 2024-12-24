import { DEBUG, GAME_SETTINGS } from '../config.js';
import ColliderManager from '../components/ColliderManager.js';
import FertilizerBall from '../components/FertilizerBall.js'
import GardenBed from '../components/GardenBed.js';

/**
 * Handles collisions in the game using 2D sphere logic.
 * @param {Array} objects - The list of game objects (e.g., balls, flower pots).
 * @param {Array} players - The list of players, each with a flower pot.
 * @param {Function} onCollision - Callback function to handle specific collision events.
 */

export default function handleCollisions(objects, players, onCollision)
{
	const balls = objects.filter((obj) => obj instanceof FertilizerBall);
	const flowerPots = players.map((player) => player.flowerPot);
	const gardenBeds = objects.filter((obj) => obj instanceof GardenBed);
	const { ballRadius, flowerPotRadius, gardenBedRadius, reboundFactor } = GAME_SETTINGS.collision;
	if (DEBUG)
	{
		balls.forEach((ball) =>
			ColliderManager.addColliderVisual(
				ball.model.parent,
				{ x: ball.model.position.x, y: 0.01, z: ball.model.position.z }, // Raise slightly to avoid z-fighting
				ballRadius,
				0xff0000
			)
		);
		flowerPots.forEach((flowerPot) =>
			ColliderManager.addColliderVisual(
				flowerPot.model.parent,
				{ x: flowerPot.model.position.x, y: 0.01, z: flowerPot.model.position.z },
				flowerPotRadius,
				0x00ff00
			)
		);
		gardenBeds.forEach((gardenBed) =>
			ColliderManager.addColliderVisual(
				gardenBed.model.parent,
				{ x: gardenBed.model.position.x, y: 0.01, z: gardenBed.model.position.z },
				gardenBedRadius,
				0x0000ff
			)
		);
	}
	balls.forEach((ball) => {
		flowerPots.forEach((flowerPot) => {
			if (ColliderManager.detect2DSphereCollision(ball.model, flowerPot.model, ballRadius, flowerPotRadius))
			{
				ball.handleCollision(flowerPot, flowerPot.velocity || new THREE.Vector3(0, 0, 0));
				onCollision(flowerPot, ball);
			}
		});
		gardenBeds.forEach((gardenBed) => {
			if (ColliderManager.detect2DSphereCollision(ball.model, gardenBed.model, ballRadius, gardenBedRadius))
				ball.handleCollision(gardenBed);
		});
		//if (!collisionOccurred)
		//	ball.lastCollidedObject = null;
	});
}