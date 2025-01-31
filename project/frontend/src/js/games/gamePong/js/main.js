// Entry point for initializing the Pong game.
// Sets up the renderer, game logic, and event listeners, and starts the animation loop.

import
{
	createRenderer, 
	setupResizeListener, 
	setupMutationObserver, 
	startAnimation 
}	from '../../shared/js/index.js';
import GameLogic from './gameLogic.js';

export async function initPong()
{
	const roomId = localStorage.getItem('roomId');
	const players = JSON.parse(localStorage.getItem('players'));
	if (!roomId || !players)
	{
		console.error("Missing game data. Redirecting to matchmaking...");
		navigateTo('matchmaking');
		return;
	}
	console.log(`Initializing game for Room ${roomId} with players:`, players);
	const container = document.getElementById('pongContainer');
	if (!container)
	{
		console.error('pongContainer element not found!');
		return ;
	}
	try
	{
		const renderer = createRenderer(container);
		const gameLogic = new GameLogic(renderer);
		const handleResize = setupResizeListener(renderer, gameLogic);
		await gameLogic.init();
		const animationId = startAnimation(gameLogic, renderer);
		setupMutationObserver(container, animationId, renderer, handleResize);
	}
	catch (error)
	{
		console.error('initPong: Error occurred:', error);
	}
}