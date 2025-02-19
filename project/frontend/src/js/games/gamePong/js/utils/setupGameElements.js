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
	const grassModel = await ModelLoader.loadModel(modelPaths.grassBlade);
	const grassInstance = new Grass(grassModel);
	const grassField = grassInstance.createGrassField();
	scene.add(grassField);
	objects.push(grassInstance);

	// create and add FertilizerBalls to the ballPool
	for (let i = 0; i < 5; i++)
	{  // preload 5 balls (adjust as needed)
		const fertilizerBall = new FertilizerBall();
		await fertilizerBall.loadModel(modelPaths.fertilizerBall);
		fertilizerBall.deactivate();
		scene.add(fertilizerBall.model);
		ballPool.push(fertilizerBall);  // sdd to the pool
	}

}