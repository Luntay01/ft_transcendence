import { loadGameSettings } from './games/gamePong/js/config.js';

export async function setupHome() {
	const userinfo = document.getElementById('userinfo');
	const access = localStorage.getItem('access');
	try {
		const response = await fetch('/api/users/me', {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${access}` }
		});
		const data = await response.json();
		if (response.ok) {
			let username = data.username;
			let email = data.email;
			let provider = data.provider;
			let img = data.picture;
			let src = `${img}`;
			let width = '50px';
			let height = '50px';
			userinfo.innerHTML = 
			`
			<div class ="top-right">
			<img src="${src}" alt="picture is not found" width=${width} height=${height}>
			</div>
			<div class="center-container">
			<p> Welcome back, ${username}!</p>
			</div>
			<div class="bottom-container">
			<p> Service Provider: ${provider} </p>
			</div>
			`
		}
	} catch (error) {
		console.log('Fail to fetch user information:', error);
	}
	const storedGameMode = localStorage.getItem("gameMode") || "4-player";
	updateGameModeButtonHighlight(storedGameMode);
	const storedMatchType = localStorage.getItem("matchType") || "ranked";
	updateMatchTypeButtonHighlight(storedMatchType);
	//window.GAME_SETTINGS.matchType = storedMatchType;
}

function updateGameModeButtonHighlight(mode) {
	const gameModeButtons = document.querySelectorAll('[id^="btn-4-player"], [id^="btn-2-player"]');
	gameModeButtons.forEach(button => button.classList.remove("active"));
	const selectedButton = document.getElementById(`btn-${mode}`);
	if (selectedButton) {
		selectedButton.classList.add("active");
	}
}

function updateGameMode(mode) {
	localStorage.setItem("gameMode", mode);
	window.GAME_SETTINGS.gameMode = mode;
	console.log(`Game mode updated to: ${mode}`);
	updateGameModeButtonHighlight(mode);
}
window.updateGameMode = updateGameMode;

function updateMatchType(type) {
	localStorage.setItem("matchType", type);
	window.GAME_SETTINGS.matchType = type;
	console.log(`Match type updated to: ${type}`);
	updateMatchTypeButtonHighlight(type);
}
window.updateMatchType = updateMatchType;

function updateMatchTypeButtonHighlight(type) {
	const buttons = document.querySelectorAll('[id^="btn-ranked"], [id^="btn-unranked"]');
	buttons.forEach(button => button.classList.remove("active"));
	const selectedButton = document.getElementById(`btn-${type}`);
	if (selectedButton) {
		selectedButton.classList.add("active");
	}
}
