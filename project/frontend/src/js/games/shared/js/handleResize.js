/**
 * Sets up a resize event listener for responsive rendering.
 * @param {THREE.WebGLRenderer} renderer - The WebGLRenderer to resize.
 * @param {GameLogic} gameLogic - The game logic instance with the camera to update.
 * @returns {Function} - The resize event handler (for cleanup purposes).
 */

export function setupResizeListener(renderer, gameLogic)
{
	const handleResize = () => {
		renderer.setSize(window.innerWidth, window.innerHeight);
		gameLogic.camera.aspect = window.innerWidth / window.innerHeight;
		gameLogic.camera.updateProjectionMatrix();
	};
	window.addEventListener('resize', handleResize);
	return handleResize;
}