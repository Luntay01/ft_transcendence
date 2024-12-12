import FlowerPot from '../components/FlowerPot.js';

/**
 * Sets up the players (flower pots) in the scene.
 * @param {THREE.Scene} scene - The Three.js scene.
 * @returns {Array} - An array of player objects.
 */

export default async function setupPlayers(scene)
{
	const positions = {
		bottom: { x: 0, y: 0, z: 10, rotationY: 0 },
		top: { x: 0, y: 0, z: -10, rotationY: Math.PI },
		right: { x: 10, y: 0, z: 0, rotationY: Math.PI / 2 },
		left: { x: -10, y: 0, z: 0, rotationY: -Math.PI / 2 },
	};
	const players = [];
	for (const positionKey in positions)
	{
		const { x, y, z, rotationY } = positions[positionKey];
		const potModel = new FlowerPot();
		const pot = await potModel.loadModel('/js/games/gamePong/assets/models/flower_pot.glb');
		pot.position.set(x, y, z);
		pot.rotation.y = rotationY; // Align the flowerpot with its position
		scene.add(pot);
		players.push({ position: positionKey, flowerPot: potModel });
	}
	return players;
}