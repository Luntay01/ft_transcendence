
class ColliderManager
{
	static detectCollision(object1, object2)
	{
		const box1 = new THREE.Box3().setFromObject(object1);
		const box2 = new THREE.Box3().setFromObject(object2);
		return box1.intersectsBox(box2);
	}
}
export default ColliderManager;