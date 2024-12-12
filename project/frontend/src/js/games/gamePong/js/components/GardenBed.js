
class GardenBed
{
	constructor()
	{
		this.model = null;
		this.loader = new THREE.GLTFLoader();
	}

	async loadModel(path)
	{
		const gltf = await this.loader.loadAsync(path);
		this.model = gltf.scene;

		// Optional: Set default scale or other properties
		this.model.scale.set(1, 1, 1);

		return this.model;
	}

	setPosition(x, y, z)
	{
		if (this.model)
			this.model.position.set(x, y, z);
	}
}

export default GardenBed;