import WebSocketService from '../../../../WebSocketService.js';
import { GAME_SETTINGS } from '../config.js';

/**
 * Registers gameplay-specific WebSocket event handlers.
 * @param {GameLogic} gameLogic - The instance of GameLogic to interact with.
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
		{
			player.flowerPot.updateState(direction, isMoving);
		}
	});

	wsService.registerEvent('ball_update', (message) => {
		console.log("Ball Update Event:", message);
		gameLogic.updateBallPosition(message.ballPosition);
	});

	wsService.registerEvent('score_update', (message) => {
		console.log("Score Update Event:", message);
		gameLogic.updateScore(message.scores);
	});

	wsService.registerEvent('game_end', (message) => {
		console.log("Game End Event:", message);
		gameLogic.endGame(message.winner);
	});
}
