/**
 * Starts the animation loop for the game.
 * @param {GameLogic} gameLogic - The game logic instance to update.
 * @param {THREE.WebGLRenderer} renderer - The WebGLRenderer to render the scene.
 * @returns {number} - The animation loop ID (used for cleanup).
 */

export function startAnimation(gameLogic, renderer)
{
	const clock = new THREE.Clock();
	function tick()
	{
		const delta = clock.getDelta();
		gameLogic.update(delta);
		renderer.render(gameLogic.scene, gameLogic.camera);
		renderer.autoClear = false; // prevent clearing the previous render
		renderer.render(gameLogic.uiScene, gameLogic.uiCamera);
		renderer.autoClear = true; // restore auto-clear
		requestAnimationFrame(tick);
	}
	return requestAnimationFrame(tick);
}