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
export async function setupGameWebSocketHandlers(gameLogic)
{
	const wsService = await ensureWebSocketService();
	const currentRoomId = localStorage.getItem('roomId');
	const disconnectedPlayers = [];
	wsService.registerEvent('player_move', (message) => {
		if (message.room_id !== currentRoomId) return;
		const { player_id, direction, isMoving } = message;
		const player = gameLogic.playerMap[player_id];
		if (!player)
		{
			console.log(`No player found with ID ${player_id}`);
			return;
		}
		if (player.flowerPot.direction !== direction || player.flowerPot.isMoving !== isMoving)
			player.flowerPot.updateState(direction, isMoving);
	});

	wsService.registerEvent("ball_updates", (message) => {
		if (message.room_id !== currentRoomId) return;
		message.balls.forEach((ballData) => {
			const ball = gameLogic.ballMap[ballData.ball_id];
			if (ball)
				ball.updateFromServer({ position: ballData.position, velocity: ballData.velocity });
		});
	});

	wsService.registerEvent('ball_update', (message) => {
		if (message.room_id !== currentRoomId) return;
		const ball = gameLogic.ballMap[message.ball_id];
		if (ball)
			ball.updateFromServer({ position: message.position, velocity: message.velocity });
	});

	wsService.registerEvent("ball_spawn", (message) => {
		if (message.room_id !== currentRoomId) return;
		let ball = gameLogic.ballPool.find(b => b.id === message.ball_id);
		if (ball)
		{
			ball.addBall(message.position, message.velocity);
			gameLogic.ballMap[message.ball_id] = ball;
		}
	});

	wsService.registerEvent("ball_despawn", (message) => {
		if (message.room_id !== currentRoomId) return;
		const ball = gameLogic.ballMap[message.ball_id];
		if (ball)
			ball.deactivate();
		gameLogic.updatePlayerScore(message.player_id, message.remaining_lives);
	});

	wsService.registerEvent('start_game_countdown', (message) => {
		if (message.room_id !== currentRoomId) return;
		console.log(`Countdown: ${message.countdown}`);
	});

	wsService.registerEvent('player_left', (message) => {
		if (message.room_id !== currentRoomId) return;
		const voterId = localStorage.getItem('player_id');
		const targetPlayerId = message.player_id;
		if (!voterId || voterId === targetPlayerId)
			return;
		if (!disconnectedPlayers.includes(targetPlayerId))
			disconnectedPlayers.push(targetPlayerId);
		updateDisconnectUI();
	});

	function updateDisconnectUI() {
		const overlay = document.getElementById("disconnectOverlay");
		const disconnectMessage = document.getElementById("disconnectMessage");
		const voteContainer = document.getElementById("voteKickButtons");
		if (!overlay || !disconnectMessage || !voteContainer)
			return;
		voteContainer.innerHTML = "";
		if (disconnectedPlayers.length === 0)
		{
			overlay.classList.remove("show");
			return;
		}
		overlay.classList.add("show");
		disconnectMessage.textContent = `Players disconnected: ${disconnectedPlayers.length}`;
		disconnectedPlayers.forEach((playerId) => {
			const voteButton = document.createElement("button");
			voteButton.className = "btn";
			voteButton.textContent = `Vote to Kick Player ${playerId}`;
			voteButton.onclick = () => {
				const voteKey = `${localStorage.getItem('player_id')}:${playerId}`;
				wsService.send("vote_kick", { 
					room_id: currentRoomId, 
					vote_key: voteKey
				});
				disconnectedPlayers.splice(disconnectedPlayers.indexOf(playerId), 1);
				updateDisconnectUI();
			};
			voteContainer.appendChild(voteButton);
		});
	}

	wsService.registerEvent("player_joined", (message) => {
		if (message.room_id !== currentRoomId) return;
		console.log(`Player reconnected: ${message.username} (ID: ${message.player_id})`);
		const index = disconnectedPlayers.indexOf(message.player_id);
		if (index !== -1) {
			disconnectedPlayers.splice(index, 1);
		}
		const disconnectOverlay = document.getElementById("disconnectOverlay");
		if (disconnectOverlay)
		{
			if (disconnectedPlayers.length === 0)
				disconnectOverlay.classList.remove("show");
		}
		else
			console.log("disconnectOverlay element not found!");
		updateDisconnectUI();
	});

	wsService.registerEvent("game_paused", (message) => {
		if (message.room_id !== currentRoomId) return;
		console.log("Game paused due to player disconnect!");
		document.getElementById("disconnectOverlay").classList.add("show");
	});
	
	wsService.registerEvent("game_resumed", (message) => {
		if (message.room_id !== currentRoomId) return;
		console.log("Game resumed!");
		if (disconnectedPlayers.length === 0)
			document.getElementById("disconnectOverlay").classList.remove("show");
	});
	
	wsService.registerEvent("player_voted_out", (message) => {
		if (message.room_id !== currentRoomId) return;
		console.log(`Player ${message.player_id} was voted out.`);
		const index = disconnectedPlayers.indexOf(message.player_id);
		if (index !== -1)
			disconnectedPlayers.splice(index, 1);
		if (disconnectedPlayers.length === 0)
			document.getElementById("disconnectOverlay").classList.remove("show");
		updateDisconnectUI();
	});
	
	wsService.registerEvent("player_eliminated", (message) => {
		if (message.room_id !== currentRoomId) return;
		console.log(`Player ${message.player_id} eliminated! Removing flowerpot...`);
		const player = gameLogic.playerMap[message.player_id];
		if (player) {
			player.flowerPot.deactivate();
			delete gameLogic.playerMap[message.player_id];
		}
		const remainingPlayers = Object.keys(gameLogic.playerMap).length;
		if (remainingPlayers === 1) {
			const winnerId = Object.keys(gameLogic.playerMap)[0];
			console.log(`Only one player remains. Declaring winner: ${winnerId}`);
			gameLogic.endGame(winnerId);
		}
	});

	wsService.registerEvent("game_state", (message) => {
		if (message.room_id !== currentRoomId) return;
		const { balls, players, eliminated_players} = message;
		balls.forEach((ballData) => {
			let ball = gameLogic.ballPool.find(b => b && b.id === ballData.ball_id);
			if (!ball)
			{
				ball = gameLogic.ballPool.find(b => !b.active);
				if (ball)
					ball.id = ballData.ball_id;
			}
			if (ball)
			{
				ball.addBall(ballData.position, ballData.velocity);
				gameLogic.ballMap[ball.id] = ball;
			}
		});
		gameLogic.ballPool.forEach(ball => {
			if (ball && !balls.some(b => b.ball_id === ball.id))
			{
				ball.deactivate();
				delete gameLogic.ballMap[ball.id];
			}
		});
		eliminated_players.forEach(playerId => {
			const player = gameLogic.playerMap[playerId];
			if (player) {
				player.flowerPot.deactivate();
				delete gameLogic.playerMap[playerId];
			}
		});
		players.forEach(playerData => {
			const player = gameLogic.playerMap[playerData.player_id];
			if (player)
			{
				player.flowerPot.model.position.set(playerData.position.x, 0, playerData.position.z);
				gameLogic.updatePlayerScore(playerData.player_id, playerData.lives);
			}
		});
	});

}

export async function ensureWebSocketService()
{
	if (!window.WebSocketService) {
		console.log("Loading WebSocketService dynamically...");
		await import('../../../../WebSocketService.js');
	}
	return WebSocketService.getInstance();
}
