import setupLighting			from './utils/setupLighting.js';
import setupPlayers				from './utils/setupPlayers.js';
import { processPlayerInput }	from "./utils/PlayerInput.js";
import setupGameElements		from './utils/setupGameElements.js';
import handleCollisions			from './utils/handleCollisions.js';
import { setupGameWebSocketHandlers, ensureWebSocketService } from './utils/GameWebSocketHandlers.js';
import { createScoreUI, updateScoreText } from './components/ScoreSprites.js';

const GAME_SETTINGS = window.GAME_SETTINGS;
let wsService = null;
(async () => { wsService = await ensureWebSocketService(); })();

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
		this.ballMap = {};
		this.ballPool = [];
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
		await setupGameElements(this.scene, this.objects, this.ballPool);
		await setupGameWebSocketHandlers(this);
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
			this.sendInitialPlayerPosition();
		}
		else//spectator view
		{
			const { position, lookAt } = GAME_SETTINGS.cameraStates.spectator;
			this.camera.position.set(position.x, position.y, position.z);
			this.camera.lookAt(lookAt.x, lookAt.y, lookAt.z);
		}
		const playerCount = this.players.length;
		this.scoreSprites = createScoreUI(this.uiScene, playerCount);
		const startingScore = GAME_SETTINGS.scoring.startingScore;
		this.players.forEach(player => {
			this.updatePlayerScore(player.playerId, startingScore);
		});
		console.log('GameLogic: Initialization complete.');
	}

	update(delta)
	{
		if (this.currentPlayer)
			processPlayerInput(this.currentPlayer);
		this.players.forEach(player => { player.flowerPot.update(delta); });
		this.objects.forEach((obj) => { if (obj.update) obj.update(delta); });
		this.ballPool.forEach(ball => { if (ball.active) ball.update(delta); });
	}

	sendInitialPlayerPosition()
	{
		if (!this.currentPlayer)
			return;
		const { x, z } = this.currentPlayer.flowerPot.model.position;
		wsService.send('player_position', { player_id: this.currentPlayer.playerId, position: { x, z } });
		this.currentPlayer.lastSentPosition = { x, z };
	}

	handleBallSpawn(data)
	{
		const availableBall = this.ballPool.find(ball => !ball.active);
		if (availableBall)
			availableBall.addBall(data.position, data.velocity);
	}

	handleBallOutOfBounds(ball)
	{
		console.log("Ball out of bounds, deactivating...");
		ball.deactivate();
	}

	onFlowerPotHit(flowerPot, ball)
	{
		const { dampingFactor, minimumSpeed } = GAME_SETTINGS.collision;
		ball.velocity.multiplyScalar(dampingFactor);
		if (ball.velocity.length() < minimumSpeed)
			ball.velocity.setLength(minimumSpeed);
	}

	updatePlayerScore(playerId, newScore)
	{
		const playerIndex = this.players.findIndex(player => String(player.playerId) === String(playerId));
		if (!this.scoreSprites || playerIndex < 0 || playerIndex >= this.scoreSprites.length)
			return;
		const { context, texture } = this.scoreSprites[playerIndex];
		updateScoreText(context, newScore);
		texture.needsUpdate = true;
	}


	async cleanup()
	{
		const ws = await ensureWebSocketService();
		if (ws.isConnected()) {
			ws.disconnect();
		}
		ws.unregisterAllEvents();
		this.ballPool.forEach(ball => ball.deactivate());
		this.ballMap = {};
		this.objects.forEach(obj => this.scene.remove(obj));
		this.objects = [];
		this.uiScene.children.forEach(obj => this.uiScene.remove(obj));
		this.players = [];
		this.playerMap = {};
		localStorage.removeItem('roomId');
		localStorage.removeItem('players');
	}


	endGame(winnerId)
	{
		const winner = this.playerMap[winnerId];
		if (winner)
		{
			localStorage.setItem("gameWinner", winnerId);
			localStorage.setItem("gameWinnerName", winner.name);
		}
		else
			localStorage.setItem("gameWinner", winnerId);
		this.cleanup();
		navigateTo('game_end');
	}
	

}

export default GameLogic;