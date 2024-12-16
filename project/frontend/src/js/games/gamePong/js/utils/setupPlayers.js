import mockUsers from "./mockUsers.js";
import FlowerPot from '../components/FlowerPot.js';

/**
 * Set up players on the field with positional constraints.
 * @param {THREE.Scene} scene - The game scene.
 * @returns {Array} - Array of players with associated flower pots.
 */

export default async function setupPlayers(scene)
{
	const positions = {
	bottom: { x: 0, y: 0, z: 10, rotationY: 0, movementDirection: "horizontal" },
	top: { x: 0, y: 0, z: -10, rotationY: Math.PI, movementDirection: "horizontal" },
	left: { x: -10, y: 0, z: 0, rotationY: -Math.PI / 2, movementDirection: "vertical" },
	right: { x: 10, y: 0, z: 0, rotationY: Math.PI / 2, movementDirection: "vertical" },
	};
	const players = [];
	for (const user of mockUsers)
	{
		const position = positions[user.flowerPotId];
		if (!position)
		{
			console.error(`Invalid flowerPotId for user: ${user.name}`);
			continue;
		}
		const { x, y, z, rotationY, movementDirection } = position;
		const flowerPot = new FlowerPot();
		const potModel = await flowerPot.loadModel('/js/games/gamePong/assets/models/flower_pot.glb');
		potModel.position.set(x, y, z);
		potModel.rotation.y = rotationY;
		scene.add(potModel);
		players.push({
			playerId: user.id,
			name: user.name,
			position: user.flowerPotId,
			controls: user.controls,
			flowerPot,
			movementDirection,
		});
	}
	return players;
}


/*
export default async function setupPlayers(scene) {
	const positions = {
	  bottom: { x: 0, y: 0, z: 10, rotationY: 0 },
	  top: { x: 0, y: 0, z: -10, rotationY: Math.PI },
	  right: { x: 10, y: 0, z: 0, rotationY: Math.PI / 2 },
	  left: { x: -10, y: 0, z: 0, rotationY: -Math.PI / 2 },
	};
  
	const players = [];
	for (const user of mockUsers) {
	  const { x, y, z, rotationY } = positions[user.flowerPotId];
	  const flowerPot = new FlowerPot();
	  const potModel = await flowerPot.loadModel('/js/games/gamePong/assets/models/flower_pot.glb');
	  potModel.position.set(x, y, z);
	  potModel.rotation.y = rotationY;
	  scene.add(potModel);
  
	  players.push({
		playerId: user.id,
		controls: user.controls,
		flowerPot,
	  });
	}
  
	return players;
}
*/
/*
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
		const { x, y, z, rotationY } = positions[user.flowerPotId];
		const potModel = new FlowerPot();
		const pot = await potModel.loadModel('/js/games/gamePong/assets/models/flower_pot.glb');
		pot.position.set(x, y, z);
		pot.rotation.y = rotationY; // Align the flowerpot with its position
		scene.add(pot);
		players.push({ position: positionKey, flowerPot: potModel });
	}
	return players;
}
*/