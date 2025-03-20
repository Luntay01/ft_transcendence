//import WebSocketService from '../../../../WebSocketService.js';
import { ensureWebSocketService } from './GameWebSocketHandlers.js';

let wsService = null;
(async () => { wsService = await ensureWebSocketService(); })();
const keyState = {};
window.addEventListener("keydown", (e) => { keyState[e.key] = true; });
window.addEventListener("keyup", (e) => { keyState[e.key] = false; });
function getCurrentKeyState() { return { ...keyState }; } // return a copy to avoid mutation issues
export function processPlayerInput(player)
{
	if (!wsService || !wsService.isConnected())
		return;
	const controls = player.controls;
	const currentKeys = getCurrentKeyState();
	let movementDirection = "neutral";
	let isMoving = false;
	if (currentKeys[controls.left]) { movementDirection = "left"; isMoving = true; } 
	if (currentKeys[controls.right]) { movementDirection = "right"; isMoving = true; }
	if (!currentKeys[controls.left] && !currentKeys[controls.right]) { movementDirection = "neutral"; isMoving = false; }
	if (movementDirection !== player.flowerPot.direction || isMoving !== player.flowerPot.isMoving)
	{
		player.flowerPot.updateState(movementDirection, isMoving);
		wsService.send('player_move', { player_id: player.playerId, direction: movementDirection, isMoving: isMoving});
	}
	if (isMoving)
	{
		const { x, z } = player.flowerPot.model.position;
		if (!player.lastSentPosition || player.lastSentPosition.x !== x || player.lastSentPosition.z !== z)
		{
			wsService.send('player_position', { player_id: player.playerId, position: { x, z } });
			player.lastSentPosition = { x, z };
		}
	}
}













//const keyState = {};

// listen for key press and release events
//window.addEventListener("keydown", (e) => { keyState[e.key] = true; });
//window.addEventListener("keyup", (e) => { keyState[e.key] = false; });

/**
 * Process player input and update the flower pot's position.
 * @param {Object} flowerPot - The flower pot to control.
 * @param {Object} controls - The player's control mappings.
 * @param {string} movementDirection - Allowed movement direction ("horizontal" or "vertical").
 */
/*
export function processPlayerInput(player)
{
	const { flowerPot, controls, position } = player;
	const speed = GAME_SETTINGS.playerConfig.speedMultiplier * 0.1;
	const boundaries = GAME_SETTINGS.playerConfig.bounds[position];
	if (!boundaries)
	{
		console.error(`Invalid position '${position}' for player.`);
		return;
	}

	let movementDirection = 'neutral';
	let isKeyHeld = false;

	if (position === 'bottom') {
		if (keyState[controls.left]) {
			flowerPot.model.position.x -= speed;
			movementDirection = 'left';
			isKeyHeld = true;
		}
		if (keyState[controls.right]) {
			flowerPot.model.position.x += speed;
			movementDirection = 'right';
			isKeyHeld = true;
		}
	} else if (position === 'top') {
		if (keyState[controls.left]) {
			flowerPot.model.position.x += speed;
			movementDirection = 'left';
			isKeyHeld = true;
		}
		if (keyState[controls.right]) {
			flowerPot.model.position.x -= speed;
			movementDirection = 'right';
			isKeyHeld = true;
		}
	} else if (position === 'left') {
		if (keyState[controls.left]) {
			flowerPot.model.position.z -= speed;
			movementDirection = 'left';
			isKeyHeld = true;
		}
		if (keyState[controls.right]) {
			flowerPot.model.position.z += speed;
			movementDirection = 'right';
			isKeyHeld = true;
		}
	} else if (position === 'right') {
		if (keyState[controls.left]) {
			flowerPot.model.position.z += speed;
			movementDirection = 'left';
			isKeyHeld = true;
		}
		if (keyState[controls.right]) {
			flowerPot.model.position.z -= speed;
			movementDirection = 'right';
			isKeyHeld = true;
		}
	}

	// clamp the position to keep within the boundaries
	flowerPot.model.position.x = THREE.MathUtils.clamp(
		flowerPot.model.position.x,
		boundaries.minX,
		boundaries.maxX
	);
	flowerPot.model.position.z = THREE.MathUtils.clamp(
		flowerPot.model.position.z,
		boundaries.minZ,
		boundaries.maxZ
	);

	// update animation state based on movement
	flowerPot.updateState(movementDirection, isKeyHeld);

}

*/