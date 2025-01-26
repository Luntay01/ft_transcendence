
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
/*

class GardenBed {
    constructor() {
        this.loader = new THREE.GLTFLoader();
    }

    async loadModel(path) {
        const gltf = await this.loader.loadAsync(path);
        return gltf.scene; // Return the loaded model directly
    }
	setPosition(x, y, z)
	{
		if (this.model)
			this.model.position.set(x, y, z);
	}
}

export default GardenBed;

*/
