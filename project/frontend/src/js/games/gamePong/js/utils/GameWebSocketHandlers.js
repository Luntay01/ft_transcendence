//import WebSocketService from '../../../../WebSocketService.js';
const GAME_SETTINGS = window.GAME_SETTINGS;
import FertilizerBall from '../components/FertilizerBall.js';

/**
 * sets up WebSocket event handlers for in-game events
 * this function registers event listeners that handle real-time game updates from the WebSocket server
 * retrieves a singleton instance of `WebSocketService`.
 * registers handlers for key game events (`player_move`, `ball_update`, `score_update`, `game_end`).
 * when the WebSocket server broadcasts an event, the corresponding handler updates the game state.
 * @param {GameLogic} gameLogic - The instance of GameLogic responsible for managing game state.
 * wsService.registerEvent('player_move', (message)	
 *	- Handles player movement updates received from the WebSocket server.
 *	- Updates the player's movement direction and state.
 *	- Ensures movement updates only happen if there is an actual change.
 */
export function setupGameWebSocketHandlers(gameLogic)
{
	const wsService = WebSocketService.getInstance();
	wsService.registerEvent('player_move', (message) => {
		const { player_id, direction, isMoving } = message;
		const player = gameLogic.playerMap[player_id];
		if (!player)
		{
			console.warn(`No player found with ID ${player_id}`);
			return;
		}
		if (player.flowerPot.direction !== direction || player.flowerPot.isMoving !== isMoving)
			player.flowerPot.updateState(direction, isMoving);
	});

	wsService.registerEvent('ball_updates', (message) => {
		message.balls.forEach((ballData) => {
			const ball = gameLogic.ballMap[ballData.ball_id];
			if (ball)
				ball.updateFromServer({ position: ballData.position, velocity: ballData.velocity });
		});
	});

	wsService.registerEvent('ball_update', (message) => {
		const ball = gameLogic.ballMap[message.ball_id];
		if (ball)
			ball.updateFromServer({ position: message.position, velocity: message.velocity });
	});

	wsService.registerEvent("ball_spawn", (message) => {
		const availableBall = gameLogic.ballPool.find(ball => !ball.active);
		if (availableBall)
		{
			availableBall.addBall(message.position, message.velocity);
			gameLogic.ballMap[message.ball_id] = availableBall;
			console.log(`Ball spawned and stored with ID: ${message.ball_id}`);
		}
	});

	wsService.registerEvent("ball_despawn", (message) => {
		const ball = gameLogic.ballMap[message.ball_id];
		if (ball)
			ball.deactivate();
		gameLogic.updatePlayerScore(message.player_id, message.remaining_lives);
	});

	wsService.registerEvent('start_game_countdown', (message) => {
		console.log(`Countdown: ${message.countdown}`);
	});

	wsService.registerEvent('score_update', (message) => {
		console.log("Score Update Event:", message);
		gameLogic.updateScore(message.scores);
	});

	wsService.registerEvent("player_eliminated", (message) => {
		console.log(`Player ${message.player_id} eliminated! Removing flowerpot...`);
		const player = gameLogic.playerMap[message.player_id];
		if (player) {
			player.flowerPot.deactivate();
			delete gameLogic.playerMap[message.player_id];
		}
		const remainingPlayers = Object.keys(gameLogic.playerMap).length;
		if (remainingPlayers === 1) {
			const winnerId = Object.keys(gameLogic.playerMap)[0]; // Get remaining player ID
			console.log(`Only one player remains. Declaring winner: ${winnerId}`);
			gameLogic.endGame(winnerId);
		}
	});
}
