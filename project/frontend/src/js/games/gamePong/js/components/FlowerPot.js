const GAME_SETTINGS = window.GAME_SETTINGS;

class FlowerPot
{
	constructor()
	{
		this.model = null;
		this.mixer = null;
		this.actions = {}; 
		this.loader = new THREE.GLTFLoader();
		this.lastDirection = 'neutral';
		this.currentState = 'neutral';
		this.speed = GAME_SETTINGS.playerConfig.speedMultiplier * 0.1;
		this.isMoving = false;
		this.direction = 'neutral';
		this.position = null;
		this.lastSentPosition = null;
		this.movementAxis = null;
		this.movementMultiplier = null;
		this.isActive = true;
	}

	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;
		this.mixer = new THREE.AnimationMixer(this.model);

		gltf.animations.forEach((clip) => {
			this.actions[clip.name] = this.mixer.clipAction(clip);
			this.actions[clip.name].clampWhenFinished = true;
			if (clip.name === 'Neutural')
				this.actions[clip.name].setLoop(THREE.LoopRepeat);
			else
				this.actions[clip.name].setLoop(THREE.LoopOnce);
		});
		this.playAnimation('Neutural');
		return this.model;
	}

	deactivate() {
		if (this.model) {
			this.model.visible = false;
		}
		this.isActive = false;
	}

	playAnimation(actionName, postAnimationNeutral = false, speed = 1.0)
	{
		if (this.currentState === actionName) return;
		Object.values(this.actions).forEach((action) => action.stop());
		const action = this.actions[actionName];
		if (action)
		{
			action.reset().setEffectiveTimeScale(speed).play();
			this.currentState = actionName;
			action.clampWhenFinished = actionName !== 'Neutural';
			action.setLoop(actionName === 'Neutural' ? THREE.LoopRepeat : THREE.LoopOnce);
			if (postAnimationNeutral) this.setupNeutralTransition(action, actionName);
		}
	}
	
	setupNeutralTransition(action, actionName)
	{
		if (this.listenerRegistered)
			this.mixer.removeEventListener('finished', this.neutralListener);
		this.neutralListener = (event) => {
			if (event.action === action)
			{
				this.neutralPending = false;
				this.playAnimation('Neutural');
			}
		};
		this.mixer.addEventListener('finished', this.neutralListener);
		this.listenerRegistered = true;
	}

	update(delta)
	{
		if (this.mixer) this.mixer.update(delta);
		if (this.isMoving && this.direction !== "neutral")
			this.move();
	}

	move()
	{
		if (this.direction === "neutral") return;
		const boundaries = GAME_SETTINGS.playerConfig.bounds[this.position];
		if (!boundaries)
		{
			console.error(`invalid boundaries for position: ${this.position}`);
			return;
		}
		this.model.position[this.movementAxis] += this.speed * this.movementMultiplier * (this.direction === "left" ? -1 : 1);
		const minBound = this.movementAxis === "x" ? boundaries.minX : boundaries.minZ;
		const maxBound = this.movementAxis === "x" ? boundaries.maxX : boundaries.maxZ;
		this.model.position[this.movementAxis] = THREE.MathUtils.clamp(this.model.position[this.movementAxis], minBound, maxBound);
	}

	updateState(direction = this.direction, isMoving = this.isMoving)
	{
		this.direction = direction;
		this.isMoving = isMoving;
		if (this.isMoving)
		{
			const tiltAnimation = this.direction === 'left' ? 'Tilt_left' : 'Tilt_right';
			if (this.currentState !== tiltAnimation)
				this.playAnimation(tiltAnimation);
		}
		else
		{
			if (this.currentState === 'Tilt_left')
				this.playAnimation('Netural_from_left', true, 2.0); // Speed up tilt back
			else if (this.currentState === 'Tilt_right')
				this.playAnimation('Netural_from_right', true, 2.0);
		}
	}

	setColor(hexColor)
	{
		if (!this.model) return;
		this.model.traverse((child) => {
			if (child.isMesh && child.material)
			{
				if (Array.isArray(child.material))
					child.material.forEach((mat) => { if (mat.color) mat.color.set(hexColor); });
				else if (child.material.color)
					child.material.color.set(hexColor);
			}
		});
	}
}

export default FlowerPot;