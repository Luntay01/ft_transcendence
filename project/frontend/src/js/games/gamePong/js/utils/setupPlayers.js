const GAME_SETTINGS = window.GAME_SETTINGS;
import mockUsers from "./mockUsers.js";
import FlowerPot from '../components/FlowerPot.js';

/**
 * Set up players on the field with positional constraints.
 * @param {THREE.Scene} scene - The game scene.
 * @returns {Array} - Array of players with associated flower pots.
 */

export default async function setupPlayers(scene, playersData)
{
	const { positions, playerColors } = GAME_SETTINGS.playerConfig;
	const flowerPotIds = ['bottom', 'top', 'left', 'right']; // Define available positions
	const controlMappings = { left: "a", right: "d" }; // Simplified controls
	console.log("Players data in setupPlayers:", playersData);
	const players = [];
	for (const [index, player] of playersData.entries())
	{
		const flowerPotId = flowerPotIds[index % flowerPotIds.length];
		const position = positions[flowerPotId];
		if (!position)
		{
			console.error(`Invalid flowerPotId for user: ${user.name}`);
			continue;
		}
		const { x, y, z, rotationY, movementDirection } = position;
		const flowerPot = new FlowerPot();
		flowerPot.position = flowerPotId;
		const potModel = await flowerPot.loadModel(GAME_SETTINGS.modelPaths.flowerPot);
		potModel.position.set(x, y, z);
		potModel.rotation.y = rotationY;
		scene.add(potModel);
		const color = playerColors[index % playerColors.length];
		flowerPot.movementAxis = (flowerPotId === "left" || flowerPotId === "right") ? "z" : "x";
		flowerPot.movementMultiplier = (flowerPotId === "left" || flowerPotId === "bottom") ? 1 : -1;
		flowerPot.setColor(color);
		const cameraState = GAME_SETTINGS.cameraStates[flowerPotId];
		players.push({
			playerId: player.player_id,
			name: player.username,
			position: flowerPotId,
			controls: controlMappings,
			flowerPot,
			movementDirection,
			cameraState,
		});
	}
	return players;
}