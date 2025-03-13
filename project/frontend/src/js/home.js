import { loadGameSettings } from './games/gamePong/js/config.js';

export async function setupHome() {
	const userinfo = document.getElementById('userinfo');
	const access = localStorage.getItem('access');
	const matchmakeButtons = document.querySelectorAll('.matchmakeButton');
	try {
		const response = await fetch('http://localhost:8000/api/users/me', {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${access}` }
		});
		const data = await response.json();
		if (response.ok) {
			let username = data.username;
			let email = data.email;
			let provider = data.provider;
			let img = data.picture;
			let src = `http://localhost:8000/${img}`;
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
			matchmakeButtons.forEach(button => {
				button.addEventListener('click', buttonHandler);
			});
		}
	} catch (error) {
		console.error('Fail to fetch user information:', error);
	}
}
async function buttonHandler(event) {
	const btnNum = event.target.getAttribute("data-btnNum");
	localStorage.setItem('game_type', btnNum);
	const game_type = localStorage.getItem('game_type');
	console.log('Game type set to:', game_type);
}

function updateGameMode(mode)
{
	localStorage.setItem("gameMode", mode);
	window.GAME_SETTINGS.gameMode = mode;
	console.log(`Game mode updated to: ${mode}`);
	const buttons = document.querySelectorAll(".btn-group button");
	buttons.forEach(button => button.classList.remove("active"));
	const selectedButton = document.getElementById(`btn-${mode}`);
	if (selectedButton)
		selectedButton.classList.add("active");
	console.log(`Game mode set to: ${mode}`, window.GAME_SETTINGS);
}

window.addEventListener("DOMContentLoaded", () => {
	const mode = localStorage.getItem("gameMode") || "4-player";
	updateGameMode(mode);
});

window.updateGameMode = updateGameMode;
