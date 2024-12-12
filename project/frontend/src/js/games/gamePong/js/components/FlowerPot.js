
class FlowerPot
{
	constructor()
	{
		this.model = null;
		this.mixer = null;
		this.actions = {}; // Store animation actions
		this.loader = new THREE.GLTFLoader();
	}

	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;
		this.mixer = new THREE.AnimationMixer(this.model);

		// Map animations to actions
		gltf.animations.forEach((clip) => { this.actions[clip.name] = this.mixer.clipAction(clip); });
		return this.model;
	}

	playAnimation(actionName)
	{
		if (this.mixer && this.actions[actionName])
		{
			Object.values(this.actions).forEach((action) => action.stop()); // Stop other animations
			this.actions[actionName].reset().play(); // Play the selected animation
		}
	}

	update(delta)
	{
		if (this.mixer) this.mixer.update(delta); // Update the mixer with the passed delta
	}
}

export default FlowerPot;