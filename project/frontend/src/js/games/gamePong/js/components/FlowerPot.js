
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
}

export default FlowerPot;