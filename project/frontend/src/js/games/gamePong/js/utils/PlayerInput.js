

const keyState = {};

// Listen for key press and release events
window.addEventListener("keydown", (e) => {
  keyState[e.key] = true;
});

window.addEventListener("keyup", (e) => {
  keyState[e.key] = false;
});

/**
 * Process player input and update the flower pot's position.
 * @param {Object} flowerPot - The flower pot to control.
 * @param {Object} controls - The player's control mappings.
 */
export function processPlayerInput(flowerPot, controls) {
  const speed = 0.1;

  // Update position based on key states
  if (keyState[controls.up]) flowerPot.model.position.z -= speed;
  if (keyState[controls.down]) flowerPot.model.position.z += speed;
  if (keyState[controls.left]) flowerPot.model.position.x -= speed;
  if (keyState[controls.right]) flowerPot.model.position.x += speed;

  // Optional: Clamp position to prevent moving out of bounds
  flowerPot.model.position.x = THREE.MathUtils.clamp(flowerPot.model.position.x, -15, 15);
  flowerPot.model.position.z = THREE.MathUtils.clamp(flowerPot.model.position.z, -10, 10);
}




/*
function handlePlayerInput(player, direction)
{
	const flowerPot = player.flowerPot;
	if (direction === 'left' || direction === 'up')
		flowerPot.playAnimation('TiltLeft');
	else if (direction === 'right' || direction === 'down')
		flowerPot.playAnimation('TiltRight');
	else
		flowerPot.playAnimation('Idle'); // Return to idle state
}
	
export default handlePlayerInput;
*/