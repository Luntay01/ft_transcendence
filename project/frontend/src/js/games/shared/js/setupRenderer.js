/**
 * Creates and configures a Three.js WebGLRenderer.
 * @param {HTMLElement} container - The DOM element to append the renderer's canvas to.
 * @returns {THREE.WebGLRenderer} - The configured WebGLRenderer instance.
 */

export function createRenderer(container)
{
	const renderer = new THREE.WebGLRenderer({ antialias: true });
	renderer.setSize(window.innerWidth, window.innerHeight);
	container.appendChild(renderer.domElement);
	return renderer;
}