/**
 * Adds lighting to the Three.js scene.
 * @param {THREE.Scene} scene - The scene to which lights will be added.
 */

export default function setupLighting(scene)
{
	const directionalLight = new THREE.DirectionalLight(0xffffff, 5);
	directionalLight.position.set(10, 10, 10);
	const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
	scene.add(ambientLight);
	scene.add(directionalLight);
		// Set background color
	scene.background = new THREE.Color(0x87ceeb);
}