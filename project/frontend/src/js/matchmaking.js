
/*
 * - retrieves the player's ID from localStorage
 * - sends a POST request to the matchmaking API to find or create a room
 * - updates the status message with matchmaking progress and results
 * - establishes a WebSocket connection using the player's ID and room ID
 * - listens for WebSocket events like `start_game` and navigates to the game screen
 * - handles errors and updates the UI accordingly
 */
let roomStatusInterval = null;

export function setupMatchmaking()
{
    const statusMessage = document.getElementById('statusMessage');
    const roomData = { players: [] };

    (async function startMatchmaking() {
        statusMessage.textContent = "Searching for a match...";
        try
        {
            const playerId = localStorage.getItem('player_id');
            if (!playerId)
            {
                statusMessage.textContent = "Error: Player ID not found. Please log in again.";
                return;
            }
            const username = localStorage.getItem('username');
            if (!username)
                console.error("Username not found");
            
            const initialRoomData = await findMatch(playerId);
            const roomId = initialRoomData.room_id;
            roomData.players = initialRoomData.players;
            updateStatusMessage(roomId, roomData.players);
            
            const ws = WebSocketService.getInstance(); // singleton WebSocket instance
            ws.connect(`ws://localhost:8765/ws?room_id=${roomId}&player_id=${playerId}&username=${username}`);
            
            ws.registerEvent('start_game', (message) => {
                console.log("Start game event received:", message);
                localStorage.setItem('roomId', message.room_id);
                localStorage.setItem('players', JSON.stringify(message.players));
                localStorage.setItem('gameMode', message.gameMode);
                if (roomStatusInterval)
                {
                    clearInterval(roomStatusInterval);
                    roomStatusInterval = null;
                }
                navigateTo('gamePong');
            });

            ws.registerEvent('player_joined', (message) => {
                console.log("Player joined event received:", message);
                const existingPlayer = roomData.players.find(player => player.id === message.player_id);
                if (!existingPlayer)
                {
                    roomData.players.push({ id: message.player_id, username: message.player_username });
                    updateStatusMessage(roomId, roomData.players);
                }
            });

            roomStatusInterval = setInterval(async () => {
                const updatedRoomData = await fetchRoomStatus(roomId);
                if (updatedRoomData)
                {
                    roomData.players = updatedRoomData.players;
                    updateStatusMessage(roomId, roomData.players);
                }
            }, 5000);
        }
        catch (error)
        {
            console.error('Error during matchmaking:', error);
            statusMessage.textContent = "An error occurred. Please try again.";
        }
    })();
}

async function fetchRoomStatus(roomId)
{
    try {
        const accessToken = localStorage.getItem('access'); // Retrieve the access token
        if (!accessToken) {
            throw new Error('Access token is missing. Please log in again.');
        }

        const response = await fetch(`/api/pong/rooms/${roomId}/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`, // Include the token
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Unauthorized: Invalid or expired token.');
            }
            throw new Error('Failed to fetch room status');
        }

        const data = await response.json();
        console.log('Updated room data:', data);
        return data;
    }
	catch (error)
	{
        console.error('Error fetching room status:', error);
    }
}
function updateStatusMessage(roomId, players)
{
	const statusMessage = document.getElementById('statusMessage');
	if (!statusMessage)
	{
		return;
	}
	const playerNames = players
		.filter(player => player.username) // Only include players with valid usernames
		.map(player => player.username)
		.join(', ');
	statusMessage.textContent = `Joined Room ${roomId} with players: ${playerNames}`;
}

async function findMatch(playerId)
{
	const response = await fetch('/api/pong/matchmaking/', {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: new URLSearchParams({ player_id: playerId, gameMode: localStorage.getItem('gameMode') || '4-player'}),
	});
	if (!response.ok)
		throw new Error('Failed to find a match. Please try again.');
	const data = await response.json();
	return data;
}

