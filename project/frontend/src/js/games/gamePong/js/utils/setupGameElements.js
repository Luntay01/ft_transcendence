import GardenBed from '../components/GardenBed.js';
import Grass from '../components/Grass.js';
import FertilizerBall from '../components/FertilizerBall.js';
import ModelLoader from '../utils/ModelLoader.js';
const GAME_SETTINGS = window.GAME_SETTINGS;



export function rotateBackgroundForPosition(position, scene) {
	const background = scene.userData.backgroundScene;
	if (!background) return;
	switch (position) {
		case 'top': background.rotation.y = Math.PI; break;
		case 'left': background.rotation.y = Math.PI / 2; break;
		case 'right': background.rotation.y = -Math.PI / 2; break;
		case 'bottom':
		default: background.rotation.y = 0; break;
	}
}


/**
 * Loads and sets up game elements like garden beds, grass, and the ball.
 * @param {THREE.Scene} scene - The Three.js scene.
 * @param {Array} objects - Array to store objects for updates.
 */
export default async function setupGameElements(scene, objects, ballPool)
{
	const { modelPaths, gardenBeds, grass, playerConfig } = GAME_SETTINGS;
	const gardenBedPositions = gardenBeds.positions;
	// load garden beds
	for (const pos of gardenBedPositions)
	{
		const gardenBed = new GardenBed();
		await gardenBed.loadModel(modelPaths.gardenBed);
		gardenBed.setPosition(pos.x, pos.y, pos.z);
		scene.add(gardenBed.model);
		objects.push(gardenBed);
	}

	// create and add grass
	// const grassModel = await ModelLoader.loadModel(modelPaths.grassBlade);
	//const grassInstance = new Grass(grassModel);
	//const grassField = grassInstance.createGrassField();
	const backgroundScene = await ModelLoader.loadModel(modelPaths.background)
	scene.add(backgroundScene);
	scene.userData.backgroundScene = backgroundScene;
	console.log("We updaintgin?");
	//objects.push(backgroundScene);

	// create and add FertilizerBalls to the ballPool
	for (let i = 0; i < 5; i++)
	{  // preload 5 balls (adjust as needed)
		const fertilizerBall = new FertilizerBall();
		await fertilizerBall.loadModel(modelPaths.fertilizerBall);
		fertilizerBall.deactivate();
		scene.add(fertilizerBall.model);
		fertilizerBall.id = i+1;
		ballPool.push(fertilizerBall);  // sdd to the pool
	}
}

