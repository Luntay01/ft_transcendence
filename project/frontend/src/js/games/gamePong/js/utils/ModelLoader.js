
const originalWarn = console.log;
console.log = function (msg, ...args) {
    if (typeof msg === 'string') {
        if (
			msg.includes('THREE.GLTFLoader: Custom UV set') ||
            msg.includes('WebScoket already connected') ||
			msg.includes('WebSocket closed intentionally')
        ) {
            return;
        }
    }
    originalWarn.call(console, msg, ...args);
};




export default class ModelLoader
{
	static loader = new THREE.GLTFLoader(); // Create a loader instance
	static async loadModel(url) {
		return new Promise((resolve, reject) => {
		this.loader.load(
			url,
			(gltf) => { resolve(gltf.scene); },
			undefined,
			(error) => { console.log('Error loading model:', error); reject(error); }
		);
		});
	}
}