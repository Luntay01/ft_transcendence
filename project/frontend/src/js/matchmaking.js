import WebSocketService from './WebSocketService.js';

/*
 * - retrieves the player's ID from localStorage
 * - sends a POST request to the matchmaking API to find or create a room
 * - updates the status message with matchmaking progress and results
 * - establishes a WebSocket connection using the player's ID and room ID
 * - listens for WebSocket events like `start_game` and navigates to the game screen
 * - handles errors and updates the UI accordingly
 */
export function setupMatchmaking()
{
	const statusMessage = document.getElementById('statusMessage');
	const matchmakeButton = document.getElementById('matchmakeButton');
	matchmakeButton.addEventListener('click', async () => {
		statusMessage.textContent = "Searching for a match...";
		try
		{
			const playerId = localStorage.getItem('player_id');
			if (!playerId)
			{
				statusMessage.textContent = "Error: Player ID not found. Please log in again.";
				return;
			}
			const roomId = await findMatch(playerId);
			statusMessage.textContent = `Joined Room ${roomId}. Waiting for the game to start...`;
			const ws = WebSocketService.getInstance(); // Singleton WebSocket instance
			ws.connect(`ws://localhost:8765/ws?room_id=${roomId}&player_id=${playerId}`);
			ws.registerEvent('start_game', (message) => {
				console.log("Start game event received:", message);
				localStorage.setItem('roomId', message.room_id);
				localStorage.setItem('players', JSON.stringify(message.players));
				navigateTo('gamePong');
			});
			ws.registerEvent('player_joined', (message) => {
				console.log("Player joined event received:", message);
				statusMessage.textContent = `Player ${message.player_username} joined Room ${message.room_id}`;
			});
		}
		catch (error)
		{
			console.error('Error during matchmaking:', error);
			statusMessage.textContent = "An error occurred. Please try again.";
		}
	});
}

async function findMatch(playerId)
{
	const response = await fetch('/api/pong/matchmaking/', {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: new URLSearchParams({ player_id: playerId }),
	});
	if (!response.ok)
		throw new Error('Failed to find a match. Please try again.');
	const data = await response.json();
	return data.room_id;
}