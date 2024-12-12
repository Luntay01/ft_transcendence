
class FertilizerBall
{
	constructor()
	{
		this.model = null;
		this.loader = new THREE.GLTFLoader();
		this.velocity = new THREE.Vector3(0, 0, 0); // Placeholder for movement
	}

	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;
		// Optional: Adjust the scale or other properties of the ball
		this.model.scale.set(0.5, 0.5, 0.5);
		return this.model;
	}

	setPosition(x, y, z)
	{
		if (this.model)
			this.model.position.set(x, y, z);
	}

	update(deltaTime)
	{
		// Update ball movement (if applicable)
		if (this.model)
			this.model.position.add(this.velocity.clone().multiplyScalar(deltaTime));
	}
}

export default FertilizerBall;