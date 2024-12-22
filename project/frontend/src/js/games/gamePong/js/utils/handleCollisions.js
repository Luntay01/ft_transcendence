import { GAME_SETTINGS } from '../config.js';
import ColliderManager from '../components/ColliderManager.js';
import FertilizerBall from '../components/FertilizerBall.js'

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
	const gardenBeds = objects.filter((obj) => obj.type === 'gardenBed');

	const { ballRadius, flowerPotRadius, gardenBedRadius, reboundFactor } = GAME_SETTINGS.collision;
	balls.forEach((ball) => {
		// check collision with flower pots
		flowerPots.forEach((flowerPot) => {
			if (ColliderManager.detect2DSphereCollision(ball.model, flowerPot.model, ballRadius, flowerPotRadius))
			{
				console.log(`collision detected: ball with flowerPot at position ${flowerPot.model.position}`);
				onCollision(flowerPot, ball);
			}
		});
		// check collision with garden beds
		gardenBeds.forEach((gardenBed) => {
			if (ColliderManager.detect2DSphereCollision(ball.model, gardenBed.model, ballRadius, gardenBedRadius))
			{
				console.log('collision detected: ball with gardenBed');
				ball.velocity.multiplyScalar(-reboundFactor); // Example: Reverse ball's velocity
			}
		});
	});
}