
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