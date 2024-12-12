import ColliderManager from '../components/ColliderManager.js';
import FertilizerBall from '../components/FertilizerBall.js'

/**
 * Handles all collisions in the game.
 * @param {Array} objects - The list of game objects (e.g., balls, flower pots).
 * @param {Array} players - The list of players, each with a flower pot.
 * @param {Function} onCollision - Callback function to handle specific collision events.
 */

export default function handleCollisions(objects, players, onCollision)
{
	const balls = objects.filter((obj) => obj instanceof FertilizerBall);
	const flowerPots = players.map((player) => player.flowerPot);
	balls.forEach((ball) => {
		flowerPots.forEach((flowerPot) => {
			const isColliding = ColliderManager.detectCollision(flowerPot.model, ball.model);
			if (isColliding)
			{
				console.log(`Collision detected: Ball with FlowerPot at position ${flowerPot.model.position}`);
				onCollision(flowerPot, ball); // Execute the callback when a collision is detected
			}
		});
	});
}