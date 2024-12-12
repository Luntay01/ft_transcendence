import GardenBed from '../components/GardenBed.js';
import Grass from '../components/Grass.js';
import FertilizerBall from '../components/FertilizerBall.js';
import ModelLoader from '../utils/ModelLoader.js';

/**
 * Loads and sets up game elements like garden beds, grass, and the ball.
 * @param {THREE.Scene} scene - The Three.js scene.
 * @param {Array} objects - Array to store objects for updates.
 */

export default async function setupGameElements(scene, objects)
{
	// load garden beds
	const gardenBed = new GardenBed();
	const gardenBedModel = await gardenBed.loadModel('/js/games/gamePong/assets/models/garden_bed.glb');
	for (let i = 0; i < 4; i++)
	{
		const bedClone = gardenBedModel.clone();
		bedClone.position.set((i % 2 === 0 ? -10 : 10), 0, (i < 2 ? -10 : 10));
		scene.add(bedClone);
	}

	// create and add grass
	const grassModel = await ModelLoader.loadModel('/js/games/gamePong/assets/models/grass_blade.glb');
	const grass = new Grass(grassModel, 80, 80);
	const grassField = grass.createGrassField();
	scene.add(grassField);
	objects.push(grass);

	// add ball
	const fertilizerBall = new FertilizerBall();
	const ball = await fertilizerBall.loadModel('/js/games/gamePong/assets/models/fertilizer_ball.glb');
	fertilizerBall.setPosition(0, 2, 0);
	scene.add(ball);
	objects.push(fertilizerBall);
}