//import ModelLoader from './utils/ModelLoader.js';
import setupLighting from './utils/setupLighting.js';
import setupPlayers from './utils/setupPlayers.js';
import { processPlayerInput } from "./utils/PlayerInput.js";
import setupGameElements from './utils/setupGameElements.js';
import handleCollisions from './utils/handleCollisions.js';

class GameLogic
{
	constructor(renderer)
	{
		this.renderer = renderer;
		this.scene = new THREE.Scene();
		this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);

		this.camera.position.set(0, 9, 16);		//bottom player
//		this.camera.position.set(0, 9, -16);	//top player
//		this.camera.position.set(-16, 9, 0);	//left player
//		this.camera.position.set(16, 9, 0);		//right player

		this.camera.lookAt(0, -4, 0);
		this.objects = []; // Store game objects for easy updates
		this.ballPositions = []; // Ball positions for grass interaction
		this.players = [];
	}

	async init()
	{
		console.log('GameLogic: Initializing...');
		setupLighting(this.scene);
		await setupGameElements(this.scene, this.objects);
		this.players = await setupPlayers(this.scene);
		console.log('GameLogic: Initialization complete.');
	}

	update(delta)
	{
		this.players.forEach((player) => {
			//const { flowerPot, controls, movementDirection } = player;
			processPlayerInput(player);
			//processPlayerInput(flowerPot, controls, movementDirection);
			player.flowerPot.update(delta);
		});
		this.objects.forEach((obj) => {
			if (obj.update) obj.update(delta);
		});
		handleCollisions(this.objects, this.players, this.onFlowerPotHit.bind(this));
	}

	onFlowerPotHit(flowerPot, ball) {
		console.log('Collision detected between flower pot and ball.');
		ball.velocity.multiplyScalar(-1); // Reflect the ball (example logic)
	}
}

export default GameLogic;












/*
import ModelLoader from './utils/ModelLoader.js';
import FlowerPot from './components/FlowerPot.js';
import FertilizerBall from './components/FertilizerBall.js';
import Grass from './components/Grass.js';
import GardenBed from './components/GardenBed.js';
import ColliderManager from './components/ColliderManager.js';
import handlePlayerInput from './utils/PlayerInput.js';

class GameLogic
{
	constructor(renderer)
	{
		this.renderer = renderer;
		this.scene = new THREE.Scene();
		this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
		this.camera.position.set(0, 9, 16); // Default position
		this.camera.lookAt(0, -4, 0);
		this.objects = []; // Store game objects for easy updates
		this.ballPositions = []; // Ball positions for grass interaction
		this.players = [];
	}

	async init()
	{
		console.log("GameLogic: Initializing...");
		// Add lighting
		const light = new THREE.DirectionalLight(0xffffff, 5);
		light.position.set(10, 10, 10);
		const ambientLight = new THREE.AmbientLight(0xffffff, 0.5); // White light with intensity 0.5
		this.scene.add(ambientLight);
		this.scene.add(light);
		this.scene.background = new THREE.Color(0x87ceeb);
		// Load models and setup game elements
		await this.loadGameElements();
		console.log("GameLogic: Initialization complete.");
	}

	async loadGameElements()
	{
		// Load garden beds
		const gardenBed = new GardenBed();
		const gardenBedModel = await gardenBed.loadModel('/js/games/gamePong/assets/models/garden_bed.glb');
		for (let i = 0; i < 4; i++) {
		const bedClone = gardenBedModel.clone(); // Clone for multiple instances
		bedClone.position.set((i % 2 === 0 ? -10 : 10), 0, (i < 2 ? -10 : 10));
		this.scene.add(bedClone);
		}

		// Create and add grass
		const grassModel = await ModelLoader.loadModel('/js/games/gamePong/assets/models/grass_blade.glb');
		const grass = new Grass(grassModel, 80, 80);
		const grassField = grass.createGrassField();
		this.scene.add(grassField);
		this.objects.push(grass);

		// Load flower pots
		this.players = await this.setupPlayers();

		// Add ball
		const fertilizerBall = new FertilizerBall();
		const ball = await fertilizerBall.loadModel('/js/games/gamePong/assets/models/fertilizer_ball.glb');
		fertilizerBall.setPosition(0, 2, 0); // Set initial position
		this.scene.add(ball);
		this.objects.push(fertilizerBall); // Add FertilizerBall to objects for updates
	}

	async setupPlayers()
	{
		const positions = {
			bottom: { x: 0, y: 0, z: 10, rotationY: 0 },
			top: { x: 0, y: 0, z: -10, rotationY: Math.PI },
			right: { x: 10, y: 0, z: 0, rotationY: Math.PI / 2 },
			left: { x: -10, y: 0, z: 0, rotationY: -Math.PI / 2 },
		};
		const players = [];
		for (const positionKey in positions)
		{
			const { x, y, z, rotationY } = positions[positionKey];
			const potModel = new FlowerPot();
			const pot = await potModel.loadModel('/js/games/gamePong/assets/models/flower_pot.glb');
			pot.position.set(x, y, z);
			pot.rotation.y = rotationY; // Align the flowerpot with its position
			this.scene.add(pot);
			players.push({ position: positionKey, flowerPot: potModel });
		}
		return players;
	}

	update(delta)
	{
		// Update all objects
		this.players.forEach((player) => { player.flowerPot.update(delta); });
		this.objects.forEach((obj) => { if (obj.update) obj.update(delta); });
		// Handle collisions and interactions
		this.handleCollisions();
	}

	handleInput(player, direction)
	{
		handlePlayerInput(player, direction);
	}

	handleCollisions()
	{
		const balls = this.objects.filter((obj) => obj instanceof FertilizerBall);
		const flowerPots = this.players.map((player) => player.flowerPot); // Assuming players have flowerpots
		balls.forEach((ball) => {
			flowerPots.forEach((flowerPot) => {
				const isColliding = ColliderManager.detectCollision(flowerPot.model, ball.model);
				if (isColliding)
				{
					console.log(`Ball hit the flower pot of player at position: ${flowerPot.model.position}`);
					// Handle collision logic, e.g.:
					this.onFlowerPotHit(flowerPot, ball);
				}
			});
		});
	}
	// Example collision handling logic
	onFlowerPotHit(flowerPot, ball)
	{
		// Update game state, e.g., score deduction, ball reflection, etc.
		console.log('Collision detected between flower pot and ball.');
		// Reflect the ball (example logic)
		ball.velocity.multiplyScalar(-1);
	}
}

export default GameLogic;

*/