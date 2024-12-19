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
}
export default ColliderManager;