import setupLighting			from './utils/setupLighting.js';
import setupPlayers				from './utils/setupPlayers.js';
import { processPlayerInput }	from "./utils/PlayerInput.js";
import setupGameElements		from './utils/setupGameElements.js';
import handleCollisions			from './utils/handleCollisions.js';
import { createScoreUI, updateScoreText } from './components/ScoreSprites.js';
import { GAME_SETTINGS }		from './config.js';

class GameLogic
{
	constructor(renderer)
	{
		//TODO: move camera logic into its own file
		this.renderer = renderer;
		this.scene = new THREE.Scene();
		const { position, lookAt } = GAME_SETTINGS.cameraStates.bottom; // change camera position here
		this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
		this.camera.position.set(position.x, position.y, position.z);
		this.camera.lookAt(lookAt.x, lookAt.y, lookAt.z);
		this.objects = []; // Store game objects for easy updates
		this.ballPositions = []; // Ball positions for grass interaction
		this.players = [];

		this.uiScene = new THREE.Scene();
		this.uiCamera = new THREE.OrthographicCamera(
			-window.innerWidth / 2, 
			window.innerWidth / 2, 
			window.innerHeight / 2, 
			-window.innerHeight / 2, 
			0.1, 
			10
			);
		this.uiCamera.position.set(0, 0, 5);
		this.uiCamera.lookAt(0, 0, 0);
	}

	async init()
	{
		console.log('GameLogic: Initializing...');
		setupLighting(this.scene);
		await setupGameElements(this.scene, this.objects);
		this.players = await setupPlayers(this.scene);
		const playerCount = this.players.length;
		this.scoreSprites = createScoreUI(this.uiScene, playerCount);
		console.log('GameLogic: Initialization complete.');
	}

	update(delta)
	{
		this.players.forEach((player, index) => {
			processPlayerInput(player);
			player.flowerPot.update(delta);
			const playerScore = GAME_SETTINGS.scoring.startingScore - Math.floor(delta); // Placeholder logic
			this.updatePlayerScore(index, playerScore);
		});
		this.objects.forEach((obj) => {
			if (obj.update) obj.update(delta);
		});
		handleCollisions(this.objects, this.players, this.onFlowerPotHit.bind(this));
	}

	onFlowerPotHit(flowerPot, ball)
	{
		const { dampingFactor, minimumSpeed } = GAME_SETTINGS.collision;
		ball.velocity.multiplyScalar(dampingFactor);
		if (ball.velocity.length() < minimumSpeed)
			ball.velocity.setLength(minimumSpeed);

	}

	updatePlayerScore(playerIndex, newScore)
	{
		if (!this.scoreSprites || playerIndex < 0 || playerIndex >= this.scoreSprites.length)
			return;
		const { context, texture } = this.scoreSprites[playerIndex];
		updateScoreText(context, newScore);
		texture.needsUpdate = true;
	}
}

export default GameLogic;