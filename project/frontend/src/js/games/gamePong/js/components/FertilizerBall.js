import { GAME_SETTINGS } from '../config.js';

class FertilizerBall
{
	constructor()
	{
		const { initialVelocity, bounds, scale, maxSpeed } = GAME_SETTINGS.ballPhysics;
		this.model = null;
		this.loader = new THREE.GLTFLoader();
		this.velocity = new THREE.Vector3(initialVelocity.x, initialVelocity.y, initialVelocity.z);
		this.bounds = bounds;
		this.scale = scale;
		this.maxSpeed = maxSpeed;
		this.lastCollisionTime = 0; // Timestamp of the last collision
		this.collisionCooldown = 0.1; // Cooldown in seconds
		this.lastCollidedObject = null;
		this.rotationAxis = new THREE.Vector3(0, 1, 0);
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
		const ballMesh = this.model.children[0]
		if (this.velocity.length() > this.maxSpeed)
			this.velocity.setLength(this.maxSpeed);
		this.velocity.y = 0; // no vertical motion
		this.model.position.add(this.velocity.clone().multiplyScalar(deltaTime));
		this.rotationAxis.set(this.velocity.z, 0, -this.velocity.x).normalize();
		const rotationAngle = this.velocity.length() * deltaTime; // Faster movement = faster rotation
		ballMesh.rotateOnAxis(this.rotationAxis, rotationAngle);
		this.checkBoundaries();
	}

	updateRotation(deltaTime)
	{
		if (!this.model || !this.model.children.length) return;
		// Assume the first child is the center transform
		const ballCenter = this.model.children[0];
		// Calculate rotation speed based on velocity
		const rotationSpeed = this.velocity.length();
		// Determine axis of rotation (perpendicular to velocity and the ground)
		const rotationAxis = this.rotationAxis || new THREE.Vector3(1, 0, 0);
		// Update the ball's rotation
		const deltaRotation = rotationSpeed * deltaTime * GAME_SETTINGS.ballPhysics.rotationMultiplier;
		ballCenter.rotateOnAxis(rotationAxis, deltaRotation);
	}

	resetRotationAfterCollision(collisionNormal)
	{
		if (!this.model || !this.model.children.length) return;

		console.log('Collision Normal:', collisionNormal);

		// Assume the first child is the ball
		const ballMesh = this.model.children[0];

		// Reflect velocity
		const reflectedVelocity = this.velocity.clone().sub(
			collisionNormal.multiplyScalar(2 * this.velocity.dot(collisionNormal))
		);

		console.log('Reflected Velocity:', reflectedVelocity);

		// Update rotation axis based on reflected velocity
		this.rotationAxis.set(reflectedVelocity.z, 0, -reflectedVelocity.x).normalize();

		console.log('Updated Rotation Axis:', this.rotationAxis);

		// Reset rotation of the ball (child object)
		ballMesh.rotation.set(0, 0, 0); // Reset rotation
	}


	checkBoundaries()
	{
		if (!this.model) return;
		let collisionNormal = null;
		if (this.model.position.x < this.bounds.minX || this.model.position.x > this.bounds.maxX)
		{
			this.velocity.x = -this.velocity.x * GAME_SETTINGS.collision.reboundFactor;
			collisionNormal = new THREE.Vector3(this.model.position.x < this.bounds.minX ? 1 : -1, 0, 0);
		}
		if (this.model.position.z < this.bounds.minZ || this.model.position.z > this.bounds.maxZ)
		{
			this.velocity.z = -this.velocity.z * GAME_SETTINGS.collision.reboundFactor;
			collisionNormal = new THREE.Vector3(0, 0, this.model.position.z < this.bounds.minZ ? 1 : -1);
		}
		if (collisionNormal)
			this.resetRotationAfterCollision(collisionNormal);
		const maxSpeed = GAME_SETTINGS.ballPhysics.maxSpeed;
		if (this.velocity.length() > maxSpeed)
			this.velocity.setLength(maxSpeed);
	}

	/**
	 * Handle collision with another object
	 * @param {Object} object - The object the ball collided with.
	 * @param {THREE.Vector3} objectVelocity - Velocity of the object (optional).
	 */
	handleCollision(object, objectVelocity = new THREE.Vector3(0, 0, 0))
	{
		if (this.lastCollidedObject === object)
			return; // skip if it's the same object
		this.lastCollidedObject = object; // update the last collided object
		const ballVelocity = this.velocity.clone();
		// calculate the normal vector at the point of collision
		const collisionNormal = new THREE.Vector3()
			.subVectors(this.model.position, object.model.position)
			.normalize();
		console.log('Collision Normal:', collisionNormal);
		// reflect the ball's velocity based on the normal
		const reflectedVelocity = ballVelocity.clone().sub(
			collisionNormal.multiplyScalar(2 * ballVelocity.dot(collisionNormal))
		);
		// object velocity for dynamic interactions (e.g., flower pots)
		reflectedVelocity.add(objectVelocity);
		// Apply damping for flower pots
//		if (object instanceof FlowerPot) {
//			const dampingFactor = 0.5; // Reduce speed to half
//			reflectedVelocity.multiplyScalar(dampingFactor);
//		}
		// adjust velocity magnitude (e.g., add spin effect or damping)
		if (reflectedVelocity.length() > this.maxSpeed)
			reflectedVelocity.setLength(this.maxSpeed);
		this.velocity.copy(reflectedVelocity);
		this.resetRotationAfterCollision(collisionNormal);
	}
}

export default FertilizerBall;