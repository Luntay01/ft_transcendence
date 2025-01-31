import setupLighting			from './utils/setupLighting.js';
import setupPlayers				from './utils/setupPlayers.js';
import { processPlayerInput }	from "./utils/PlayerInput.js";
import setupGameElements		from './utils/setupGameElements.js';
import handleCollisions			from './utils/handleCollisions.js';
import { setupGameWebSocketHandlers } from './utils/GameWebSocketHandlers.js';
import { createScoreUI, updateScoreText } from './components/ScoreSprites.js';
import { GAME_SETTINGS }		from './config.js';

class GameLogic
{
	constructor(renderer)
	{
		//TODO: move camera logic into its own file
		this.renderer = renderer;
		this.scene = new THREE.Scene();
		const { position, lookAt } = GAME_SETTINGS.cameraStates.bottom;
		this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
		this.camera.position.set(position.x, position.y, position.z);
		this.camera.lookAt(lookAt.x, lookAt.y, lookAt.z);
		this.objects = [];
		this.ballPositions = [];
		this.players = [];
		this.playerMap = {};
		this.currentPlayer = null;

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
		setupGameWebSocketHandlers(this);
		const players = JSON.parse(localStorage.getItem('players'))
		this.players = await setupPlayers(this.scene, players);
		this.playerMap = this.players.reduce((map, player) => { map[player.playerId] = player; return map; }, {});
		console.log("Populated playerMap:", this.playerMap);
		const currentPlayerId = localStorage.getItem('player_id');
		this.currentPlayer = this.playerMap[currentPlayerId];
		if (this.currentPlayer)
		{
			const { position, lookAt } = this.currentPlayer.cameraState;
			this.camera.position.set(position.x, position.y, position.z);
			this.camera.lookAt(lookAt.x, lookAt.y, lookAt.z);
		}
		else//spectator view
		{
			const { position, lookAt } = GAME_SETTINGS.cameraStates.spectator;
			this.camera.position.set(position.x, position.y, position.z);
			this.camera.lookAt(lookAt.x, lookAt.y, lookAt.z);
		}
		const playerCount = this.players.length;
		this.scoreSprites = createScoreUI(this.uiScene, playerCount);
		console.log('GameLogic: Initialization complete.');
	}

	update(delta)
	{
		if (this.currentPlayer)
			processPlayerInput(this.currentPlayer);
		this.players.forEach(player => { player.flowerPot.update(delta); });
		this.objects.forEach((obj) => { if (obj.update) obj.update(delta); });
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