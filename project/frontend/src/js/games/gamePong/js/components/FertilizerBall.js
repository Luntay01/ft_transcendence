const GAME_SETTINGS = window.GAME_SETTINGS;

class FertilizerBall
{
	constructor()
	{
		const { scale } = GAME_SETTINGS.ballPhysics;
		this.model = null;
		this.loader = new THREE.GLTFLoader();
		this.velocity = new THREE.Vector3(); // will be set from server
		this.targetPosition = new THREE.Vector3();
		this.lastServerUpdate = performance.now();
		this.lerpFactor = 0.1; // controls interpolation smoothness
		this.id = null;
		this.scale = scale;
		this.rotationAxis = new THREE.Vector3(0, 1, 0);
	}
	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;
		this.model.scale.set(this.scale, this.scale, this.scale);
		this.model.visible = false;
		return this.model;
	}
	addBall(position, velocity)
	{
		if (!this.model)
		{
			console.warn("ball model not loaded yet. delaying spawn...");
			setTimeout(() => this.addBall(position, velocity), 100);
			return;
		}
		console.log("adding Ball at position:", position);
		this.model.visible = true;
		this.model.position.set(position.x, position.y, position.z);
		this.velocity.set(velocity.x, velocity.y, velocity.z);
		this.active = true;
	}

	deactivate()
	{
		if (this.model)
		{
			this.model.visible = false;
			this.active = false;
		}
	}

	update(deltaTime)
	{
		if (!this.model) return;
		const lerpSpeed = GAME_SETTINGS.ballPhysics.lerpSpeed || 0.1;
		this.model.position.lerp(this.targetPosition, 0.5);
		//this.velocity.y = 0;//dont for that you changed this
		const ballMesh = this.model.children[0];
		if (this.velocity.length() > 0)
		{
			this.rotationAxis.set(this.velocity.z, 0, -this.velocity.x).normalize();
			const rotationAngle = this.velocity.length() * deltaTime;
			ballMesh.rotateOnAxis(this.rotationAxis, rotationAngle);
		}
	}

	updateFromServer(data)
	{
		if (!this.model) return;
		if (!this.model.position) { console.warn("Model position not available."); return; }
	
		this.targetPosition.set(data.position.x, data.position.y, data.position.z);
		this.velocity.set(data.velocity.x, data.velocity.y, data.velocity.z);
	
		//console.log(`🎯 Updated Ball Position: X=${data.position.x}, Y=${data.position.y}, Z=${data.position.z}`);
		//console.log(`💨 Updated Ball Velocity: X=${data.velocity.x}, Y=${data.velocity.y}, Z=${data.velocity.z}`);
	}
}

export default FertilizerBall;


/*
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
		const ballMesh = this.model.children[0];
		const reflectedVelocity = this.velocity.clone().sub(
			collisionNormal.multiplyScalar(2 * this.velocity.dot(collisionNormal))
		);
		this.rotationAxis.set(reflectedVelocity.z, 0, -reflectedVelocity.x).normalize();
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
		// reflect the ball's velocity based on the normal
		const reflectedVelocity = ballVelocity.clone().sub(
			collisionNormal.multiplyScalar(2 * ballVelocity.dot(collisionNormal))
		);
		// object velocity for dynamic interactions (e.g., flower pots)
		reflectedVelocity.add(objectVelocity);
		if (reflectedVelocity.length() > this.maxSpeed)
			reflectedVelocity.setLength(this.maxSpeed);
		this.velocity.copy(reflectedVelocity);
		this.resetRotationAfterCollision(collisionNormal);
	}
}

export default FertilizerBall;

*/