export async function setupEndTournScreen()
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
		console.error("No access token found. User may not be logged in.");
		return;
	}
	try {
		tourn_send_signal();
		const response = await fetch(`/api/pong/match_results/winner/${winnerId}/`, {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' }
		});
		if (!response.ok)
		{
			if (response.status === 401)
				console.warn("Unauthorized request. Token may be invalid or expired.");
			else
				console.error("Failed to fetch match results:", response.statusText);
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
		function sleep(ms) {
			return new Promise(resolve => setTimeout(resolve, ms));
		}
		await sleep(5000);
		console.log("Game End Screen Loaded. Winner:", winnerName);
		console.log("match completed, starting next match");
		//navigateTo('gamePong');
	}
	catch (error)
	{
		console.error("Error loading match results:", error);
		if (winnerNameElement)
			winnerNameElement.textContent = `🏆 Winner: Player ${winnerId}`;
	}
}
async function tourn_send_signal(){
	const responses = await fetch(`/api/pong/tournpage_response/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: new URLSearchParams({ room_id : localStorage.getItem('room_id'), signal: 1 }),
	});
	if (!responses.ok){
		const errorText = await responses.text();
		console.error("Server responded with an error:", responses.status, errorText);
		throw new Error('Failed to send signal, Please try again.');
	}
	const data = await responses.json();
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