
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
	}

	updateState(direction, isKeyHeld)
	{
		if (isKeyHeld)
		{
			const tiltAnimation = direction === 'left' ? 'Tilt_left' : 'Tilt_right';
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
}

export default FlowerPot;

/*
	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;
		this.mixer = new THREE.AnimationMixer(this.model);
		gltf.animations.forEach((clip) => {
			this.actions[clip.name] = this.mixer.clipAction(clip);
			if (clip.name === 'Neutural')
				this.actions[clip.name].setLoop(THREE.LoopRepeat);
			else
				this.actions[clip.name].setLoop(THREE.LoopOnce);
		});
		this.playAnimation('Neutural');
		return this.model;
	}

	playAnimation(actionName)
	{
		if (this.currentState === actionName) return;
		Object.values(this.actions).forEach((action) => action.stop());
		if (this.actions[actionName])
		{
			this.actions[actionName].reset().play();
			this.currentState = actionName;
			if (actionName !== 'Neutural')
			{
				this.actions[actionName].clampWhenFinished = true;
				this.actions[actionName].setEffectiveTimeScale(1);
			}
		}
	}

	update(delta)
	{
		if (this.mixer) this.mixer.update(delta); // Update the mixer with the passed delta
	}

	updateState(direction)
	{
		if (direction === 'left')
			this.playAnimation('Tilt_left');
		else if (direction === 'right')
			this.playAnimation('Tilt_right');
		else if (direction === 'neutral_left')
			this.playAnimation('Netural_from_left');
		else if (direction === 'neutral_right')
			this.playAnimation('Netural_from_right');
		else
			this.playAnimation('Neutural');
	}

*/
