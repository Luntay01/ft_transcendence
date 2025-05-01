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
import { getWebsocketURI } from '../../../utility.js'

//import WebSocketService from '../../../WebSocketService.js'
import { ensureWebSocketService } from './utils/GameWebSocketHandlers.js';

//const GAME_SETTINGS = window.GAME_SETTINGS;



export async function initPong()
{
	const roomId = localStorage.getItem('roomId');
	const players = JSON.parse(localStorage.getItem('players'));
	const playerId = localStorage.getItem('player_id');
	const username = localStorage.getItem('username');
	if (!roomId || !players|| !playerId)
	{
		console.log("Missing game data. Redirecting to matchmaking...");
		navigateTo('matchmaking');
		return;
	}
	console.log(`Initializing game for Room ${roomId} with players:`, players);
	//  reconnect WebSocket
	const ws = await ensureWebSocketService();
	ws.connect(getWebsocketURI(`/ws/connect?room_id=${roomId}&player_id=${playerId}&username=${username}`));
	const container = document.getElementById('pongContainer');
	if (!container)
	{
		console.log('pongContainer element not found!');
		return ;
	}
	try
	{
		//await loadGameSettings();
		const renderer = createRenderer(container);
		const gameLogic = new GameLogic(renderer);
		window.game = gameLogic;
		const handleResize = setupResizeListener(renderer, gameLogic);
		await gameLogic.init();
		const animationId = startAnimation(gameLogic, renderer);
		setupMutationObserver(container, animationId, renderer, handleResize);
	}
	catch (error)
	{
		console.log('initPong: Error occurred:', error);
	}
}
