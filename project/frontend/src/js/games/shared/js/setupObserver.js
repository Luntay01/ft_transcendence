/**
 * Sets up a MutationObserver to clean up resources when the game container is removed.
 * @param {HTMLElement} container - The game container element.
 * @param {number} animationId - The ID of the animation loop to cancel.
 * @param {THREE.WebGLRenderer} renderer - The WebGLRenderer to dispose of.
 * @param {Function} handleResize - The resize handler to remove.
 */

export function setupMutationObserver(container, animationId, renderer, handleResize)
{
	const observer = new MutationObserver((mutations) => {
		mutations.forEach((mutation) => {
			if (mutation.removedNodes)
			{
				mutation.removedNodes.forEach((node) => {
					if (node === container) {
						console.log('Cleaning up Pong...');
						cancelAnimationFrame(animationId);
						renderer.dispose();
						window.removeEventListener('resize', handleResize);
						observer.disconnect();
					}
				});
			}
		});
	});
	const appContainer = document.getElementById('app');
	observer.observe(appContainer, { childList: true });
}