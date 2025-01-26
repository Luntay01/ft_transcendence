/**
 * Detects collision between two objects on the XZ plane using their positions and radii.
 * @param {THREE.Object3D} object1 - First object (e.g., ball or flowerpot).
 * @param {THREE.Object3D} object2 - Second object (e.g., flowerpot or garden bed).
 * @param {number} radius1 - Radius of the first object.
 * @param {number} radius2 - Radius of the second object.
 * @returns {boolean} - True if a collision is detected, false otherwise.
 */

class ColliderManager
{
	static detect2DSphereCollision(object1, object2, radius1, radius2)
	{
		const pos1 = object1.position;
		const pos2 = object2.position;
		const distanceSquared = (pos1.x - pos2.x) ** 2 + (pos1.z - pos2.z) ** 2;
		const combinedRadius = radius1 + radius2;
		return distanceSquared < combinedRadius * combinedRadius;
	}

	/**
	 * Visualizes a 2D collider as a circle.
	 * @param {THREE.Scene} scene - The scene to which the visual should be added.
	 * @param {THREE.Vector3} position - The position of the collider center.
	 * @param {number} radius - The radius of the collider.
	 * @param {number} color - The color of the visual (e.g., 0xff0000 for red).
	 */
	static addColliderVisual(scene, position, radius, color = 0xff0000)
	{
		const geometry = new THREE.CircleGeometry(radius, 32); // 32 segments for smooth circle
		const material = new THREE.MeshBasicMaterial({
			color,
			wireframe: true,
		});
		const circle = new THREE.Mesh(geometry, material);
		// Set position and align with the XZ plane
		circle.position.set(position.x, position.y, position.z); // Slightly above ground to avoid z-fighting
		circle.rotation.x = -Math.PI / 2; // Align with the ground plane
		scene.add(circle);
		return circle;
	}

}
export default ColliderManager;