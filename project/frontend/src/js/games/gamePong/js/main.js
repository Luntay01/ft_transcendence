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

//import WebSocketService from '../../../WebSocketService.js'

//const GAME_SETTINGS = window.GAME_SETTINGS;

export async function initPong()
{
	const roomId = localStorage.getItem('roomId');
	const players = JSON.parse(localStorage.getItem('players'));
	const playerId = localStorage.getItem('player_id');
	const username = localStorage.getItem('username');
	const game_type = localStorage.getItem('game_type');
	if (!roomId || !players|| !playerId || !game_type)
	{
		console.error("Missing game data. Redirecting to matchmaking...");
		navigateTo('matchmaking');
		return;
	}
	console.log(`Initializing game for Room ${roomId} with players:`, players);
	//  reconnect WebSocket
	const ws = WebSocketService.getInstance();
	ws.connect(`ws://localhost:8765/ws?room_id=${roomId}&player_id=${playerId}&username=${username}`);
	const container = document.getElementById('pongContainer');
	if (!container)
	{
		console.error('pongContainer element not found!');
		return ;
	}
	try
	{
		//await loadGameSettings();
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