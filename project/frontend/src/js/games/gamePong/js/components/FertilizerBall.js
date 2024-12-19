
class FertilizerBall
{
	constructor()
	{
		this.model = null;
		this.loader = new THREE.GLTFLoader();
		this.velocity = new THREE.Vector3(1.5, 0, 1.2); // placeholder for movement
		this.bounds = { minX: -2, maxX: 2, minZ: -20, maxZ: 20 };
	}

	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;
		this.model.scale.set(0.9, 0.9, 0.9); // scale the ball
		return this.model;
	}

	setPosition(x, y, z)
	{
		if (this.model)
			this.model.position.set(x, y, z);
	}

	update(deltaTime)
	{
		if (!this.model) return;
		if (this.model)
		{
			this.velocity.y = 0;
			this.model.position.add(this.velocity.clone().multiplyScalar(deltaTime));
		}
		this.checkBoundaries();
	}

	checkBoundaries() {
		if (!this.model) return;

		// reflect on boundaries
		if (this.model.position.x < this.bounds.minX || this.model.position.x > this.bounds.maxX) {
			this.velocity.x = -this.velocity.x;
		}

		if (this.model.position.z < this.bounds.minZ || this.model.position.z > this.bounds.maxZ) {
			this.velocity.z = -this.velocity.z;
		}
	}
}

export default FertilizerBall;