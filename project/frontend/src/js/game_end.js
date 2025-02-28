export function setupEndGameScreen()
{
	const winnerId = localStorage.getItem("gameWinner");
	const winnerName = localStorage.getItem("gameWinnerName") || `Player ${winnerId}`;
	const winnerNameElement = document.getElementById("winnerName");

	if (winnerNameElement)
		winnerNameElement.textContent = `🏆 Winner: ${winnerName}`;
	else
		console.warn("winnerName element not found!");

	console.log("Game End Screen Loaded. Winner:", winnerName);
}