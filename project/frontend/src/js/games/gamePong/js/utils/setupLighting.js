const GAME_SETTINGS = window.GAME_SETTINGS;

/**
 * Adds lighting to the Three.js scene.
 * @param {THREE.Scene} scene - The scene to which lights will be added.
 */

export default function setupLighting(scene)
{
	const { directionalLight, ambientLight, backgroundColor } = GAME_SETTINGS.lighting;
	const dirLight = new THREE.DirectionalLight(directionalLight.color, directionalLight.intensity);
	dirLight.position.set(
		directionalLight.position.x,
		directionalLight.position.y,
		directionalLight.position.z
	);
	scene.add(dirLight);
	const ambLight = new THREE.AmbientLight(ambientLight.color, ambientLight.intensity);
	scene.add(ambLight);
	scene.background = new THREE.Color(backgroundColor);
}