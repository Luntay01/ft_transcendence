import GardenBed from '../components/GardenBed.js';
import Grass from '../components/Grass.js';
import FertilizerBall from '../components/FertilizerBall.js';
import ModelLoader from '../utils/ModelLoader.js';
import { GAME_SETTINGS } from '../config.js';

/**
 * Loads and sets up game elements like garden beds, grass, and the ball.
 * @param {THREE.Scene} scene - The Three.js scene.
 * @param {Array} objects - Array to store objects for updates.
 */

export default async function setupGameElements(scene, objects)
{
	const { modelPaths, grass, playerConfig } = GAME_SETTINGS;
	// load garden beds
	for (let i = 0; i < 4; i++)
	{
		const gardenBed = new GardenBed();
		await gardenBed.loadModel(modelPaths.gardenBed);
		//gardenBed.position.set((i % 2 === 0 ? -10 : 10), 0, (i < 2 ? -10 : 10));//TODO: remove hardcorded gardenBed offset use GAMESETTINGS instead using player bounds plus model offset
		gardenBed.setPosition((i % 2 === 0 ? -10 : 10), 0, (i < 2 ? -10 : 10));
		scene.add(gardenBed.model);;
		objects.push(gardenBed);
	}

	// create and add grass
	const grassModel = await ModelLoader.loadModel(modelPaths.grassBlade);
	const grassInstance = new Grass(grassModel);
	const grassField = grassInstance.createGrassField();
	scene.add(grassField);
	objects.push(grassInstance);

	// add ball
	const fertilizerBall = new FertilizerBall();
	const ball = await fertilizerBall.loadModel(modelPaths.fertilizerBall);
	fertilizerBall.setPosition(0, 0, 0);
	scene.add(ball);
	objects.push(fertilizerBall);
}