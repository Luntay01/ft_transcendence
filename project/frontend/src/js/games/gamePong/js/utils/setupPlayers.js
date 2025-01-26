import { GAME_SETTINGS } from '../config.js';
import mockUsers from "./mockUsers.js";
import FlowerPot from '../components/FlowerPot.js';

/**
 * Set up players on the field with positional constraints.
 * @param {THREE.Scene} scene - The game scene.
 * @returns {Array} - Array of players with associated flower pots.
 */

export default async function setupPlayers(scene)
{
	const { positions, playerColors } = GAME_SETTINGS.playerConfig;
	const players = [];
	for (const [index, user] of mockUsers.entries())
	{
		const position = positions[user.flowerPotId];
		if (!position)
		{
			console.error(`Invalid flowerPotId for user: ${user.name}`);
			continue;
		}
		const { x, y, z, rotationY, movementDirection } = position;
		const flowerPot = new FlowerPot();
		const potModel = await flowerPot.loadModel(GAME_SETTINGS.modelPaths.flowerPot);
		potModel.position.set(x, y, z);
		potModel.rotation.y = rotationY;
		scene.add(potModel);
		const color = playerColors[index % playerColors.length];
		flowerPot.setColor(color);
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