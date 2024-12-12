
export default class ModelLoader
{
	static loader = new THREE.GLTFLoader(); // Create a loader instance
	static async loadModel(url) {
		return new Promise((resolve, reject) => {
		this.loader.load(
			url,
			(gltf) => { resolve(gltf.scene); },
			undefined,
			(error) => { console.error('Error loading model:', error); reject(error); }
		);
		});
	}
}