import { GAME_SETTINGS } from '../config.js';

class FertilizerBall
{
	constructor()
	{
		const { initialVelocity, bounds, scale } = GAME_SETTINGS.ballPhysics;
		this.model = null;
		this.loader = new THREE.GLTFLoader();
		this.velocity = new THREE.Vector3(initialVelocity.x, initialVelocity.y, initialVelocity.z);
		this.bounds = bounds;
		this.scale = scale;
	}

	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;
		this.model.scale.set(this.scale, this.scale, this.scale); // scale the ball
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
		const maxSpeed = GAME_SETTINGS.ballPhysics.maxSpeed;
		if (this.velocity.length() > maxSpeed)
			this.velocity.setLength(maxSpeed);
		this.velocity.y = 0; // no vertical motion
		this.model.position.add(this.velocity.clone().multiplyScalar(deltaTime));
		this.checkBoundaries();
	}

	checkBoundaries() {
		if (!this.model) return;

		// reflect on boundaries
		if (this.model.position.x < this.bounds.minX || this.model.position.x > this.bounds.maxX)
			this.velocity.x = -this.velocity.x * GAME_SETTINGS.collision.reboundFactor;
		if (this.model.position.z < this.bounds.minZ || this.model.position.z > this.bounds.maxZ)
			this.velocity.z = -this.velocity.z * GAME_SETTINGS.collision.reboundFactor;
		const maxSpeed = GAME_SETTINGS.ballPhysics.maxSpeed;
		if (this.velocity.length() > maxSpeed)
			this.velocity.setLength(maxSpeed);
	}
}

export default FertilizerBall;