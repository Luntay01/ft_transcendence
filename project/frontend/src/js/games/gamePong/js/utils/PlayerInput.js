import mockUsers from './mockUsers.js'; 

const keyState = {};

// listen for key press and release events
window.addEventListener("keydown", (e) => { keyState[e.key] = true; });
window.addEventListener("keyup", (e) => { keyState[e.key] = false; });

/**
 * Process player input and update the flower pot's position.
 * @param {Object} flowerPot - The flower pot to control.
 * @param {Object} controls - The player's control mappings.
 * @param {string} movementDirection - Allowed movement direction ("horizontal" or "vertical").
 */


export function processPlayerInput(player)
{
	const { flowerPot, controls, position } = player;
	const speed = 0.1;
	const boundaries = {
	  bottom: { minX: -7, maxX: 7, minZ: 8, maxZ: 12 },
	  top: { minX: -7, maxX: 7, minZ: -12, maxZ: -8 },
	  left: { minX: -12, maxX: -8, minZ: -7, maxZ: 7 },
	  right: { minX: 8, maxX: 12, minZ: -7, maxZ: 7 },
	}[position];





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
		if (keyState[controls.up]) {
			flowerPot.model.position.z -= speed;
			movementDirection = 'left';
			isKeyHeld = true;
		}
		if (keyState[controls.down]) {
			flowerPot.model.position.z += speed;
			movementDirection = 'right';
			isKeyHeld = true;
		}
	} else if (position === 'right') {
		if (keyState[controls.up]) {
			flowerPot.model.position.z += speed;
			movementDirection = 'left';
			isKeyHeld = true;
		}
		if (keyState[controls.down]) {
			flowerPot.model.position.z -= speed;
			movementDirection = 'right';
			isKeyHeld = true;
		}
	}

	// Clamp the position to keep within the boundaries
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

	// Update animation state based on movement
	flowerPot.updateState(movementDirection, isKeyHeld);








/*
	let movementDirection = null;
	if (position === 'bottom')
	{
		if (keyState[controls.left])
		{
			flowerPot.model.position.x -= speed;
			movementDirection = 'left';
		}
		if (keyState[controls.right])
		{
			flowerPot.model.position.x += speed;
			movementDirection = 'right';
		}
	}
	else if (position === 'top')
	{
		if (keyState[controls.left]) {
			flowerPot.model.position.x += speed;
			movementDirection = 'left';
		}
		if (keyState[controls.right])
		{
			flowerPot.model.position.x -= speed;
			movementDirection = 'right';
		}
	}
	else if (position === 'left')
	{
		if (keyState[controls.up])
		{
			flowerPot.model.position.z -= speed;
			movementDirection = 'left';
		}
		if (keyState[controls.down])
		{
			flowerPot.model.position.z += speed;
			movementDirection = 'right';
		}
	}
	else if (position === 'right')
	{
		if (keyState[controls.up])
		{
			flowerPot.model.position.z += speed;
			movementDirection = 'left';
		}
		if (keyState[controls.down])
		{
			flowerPot.model.position.z -= speed;
			movementDirection = 'right';
		}
	}
	flowerPot.model.position.x = THREE.MathUtils.clamp(flowerPot.model.position.x, boundaries.minX, boundaries.maxX);
	flowerPot.model.position.z = THREE.MathUtils.clamp(flowerPot.model.position.z, boundaries.minZ, boundaries.maxZ);
	flowerPot.updateState(movementDirection || 'neutral');
*/
}





/*
export function processPlayerInput(flowerPot, controls, movementDirection)
{
	const speed = 0.1;
	// Define boundaries based on flowerPot's position
	let boundaries;
	switch (flowerPot.position)
	{
		case "bottom":
			boundaries = { minX: -10, maxX: 10, minZ: 8, maxZ: 12 };
			break;
		case "top":
			boundaries = { minX: -8, maxX: 8, minZ: -12, maxZ: 8 };
			break;
		case "left":
			boundaries = { minX: -12, maxX: -8, minZ: -10, maxZ: 10 };
			break;
		case "right":
			boundaries = { minX: 8, maxX: 12, minZ: -10, maxZ: 10 };
			break;
		default:
			boundaries = { minX: -10, maxX: 10, minZ: -10, maxZ: 10 };
	}
	// Update position
	if (movementDirection === "horizontal")
	{
		if (keyState[controls.left]) flowerPot.model.position.x -= speed;
		if (keyState[controls.right]) flowerPot.model.position.x += speed;
	}
	
	if (movementDirection === "vertical")
	{
		if (keyState[controls.up]) flowerPot.model.position.z -= speed;
		if (keyState[controls.down]) flowerPot.model.position.z += speed;
	}
	
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
}
*/