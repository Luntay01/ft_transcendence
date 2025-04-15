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
			document.getElementById("userGreeting").textContent = `Welcome back, ${username}!`;
			document.getElementById("profilePicture").innerHTML = `<img src="${src}" alt="picture is not found" width=${width} height=${height}>`;
			document.getElementById("serviceProvider").textContent = `Service Provider: ${provider}`;
		}
	} catch (error) {
		console.error('Fail to fetch user information:', error);
	}
	const storedGameMode = localStorage.getItem("gameMode") || "4-player";
	updateGameModeButtonHighlight(storedGameMode);
}

function updateGameModeButtonHighlight(mode) {
	const buttons = document.querySelectorAll(".btn-group button");
	buttons.forEach(button => button.classList.remove("active"));
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
