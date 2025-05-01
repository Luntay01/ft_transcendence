export async function setupEndGameScreen()
{
	const winnerId = localStorage.getItem("gameWinner");
	const accessToken = localStorage.getItem("access"); 
	const winnerNameElement = document.getElementById("winnerName");
	const matchDetailsElement = document.getElementById("matchDetails");
	if (!winnerId)
	{
		console.warn("No winner ID found in localStorage.");
		return;
	}
	if (!accessToken)
	{
		console.log("No access token found. User may not be logged in.");
		return;
	}
	try {
		const response = await fetch(`/api/pong/match_results/winner/${winnerId}/`, {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' }
		});
		if (!response.ok)
		{
			if (response.status === 401)
				console.warn("Unauthorized request. Token may be invalid or expired.");
			else
				console.log("Failed to fetch match results:", response.statusText);
			return;
		}
		const matchData = await response.json();
		const winnerName = matchData.winner.username || `Player ${winnerId}`;
		if (winnerNameElement)
			winnerNameElement.textContent = `🏆 Winner: ${winnerName}`;
		if (matchDetailsElement)
		{
			const reversedOrder = [...matchData.elimination_order].reverse();
			matchDetailsElement.innerHTML = `
				<h3>Match Summary</h3>
				<p>Room ID: ${matchData.room_id}</p>
				<ul>
					${matchData.players.map((player) => {
						const placementIndex = reversedOrder.indexOf(player.id.toString());
						const placement = placementIndex !== -1 ? placementIndex + 1 : 1;
						return `<li><strong>${getOrdinal(placement)}</strong> - ${player.username} 🏆 ${player.trophies} trophies</li>`;
					}).join('')}
				</ul>
			`;
		}
		console.log("Game End Screen Loaded. Winner:", winnerName);
	}
	catch (error)
	{
		console.log("Error loading match results:", error);
		if (winnerNameElement)
			winnerNameElement.textContent = `🏆 Winner: Player ${winnerId}`;
	}
}

function getOrdinal(n) {
	if (n % 100 >= 11 && n % 100 <= 13) return `${n}th`;
	switch (n % 10)
	{
		case 1: return `${n}st`;
		case 2: return `${n}nd`;
		case 3: return `${n}rd`;
		default: return `${n}th`;
	}
}