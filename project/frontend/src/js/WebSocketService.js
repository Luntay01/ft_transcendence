/*
 * handles websocket connections and event management
 * this singleton class ensures only one WebSocket connection is active per client
 * establishes a connection with the websocket server when matchmaking is successful
 * sends player actions (e.g., movement) to the server
 * listens for game-related events and forwards them to appropriate handlers
 * works with `GameWebSocketHandlers.js` to process incoming events
 * 
 * static getInstance()				returns the singleton instance of Websocket Service Ensures only one instance exists at any time
 * 
 * connect(url)						Establishes a WebSocket connection to the server
 * 	-this.ws = new WebSocket(url);	-Create a new WebSocket connection to the given URL
 * 	-this.ws.onopen					-Event triggered when the WebSocket connection is successfully established
 *	-this.ws.onmessage				-event triggered when a WebSocket message is received from the server
 *									-parses the incoming JSON message
 *									-Extracts the event type
 *									-finds and executes all registered handlers for that event
 *									-@param {MessageEvent} event - WebSocket message event containing data
 *	-this.ws.onclose				-event triggered when the WebSocket connection is closed
 *	-this.ws.onerror				-event triggered when an error occurs with the WebSocket connection
 *
 * disconnect()						Disconnects the WebSocket connection.
 * 
 * registerEvent(event, handler)	Registers an event listener for ws-messages 
 * 									@param {string} event the event name 
 * 									@param {Function} handler The function to call when the event occurs 
 * 									like wsService.registerEvent('player_move', (message)-from `GameWebSocketHandlers.js`
 * 
 * unregisterEvent(event, handler)	Unregisters an event listener. 
 * 
 * send(event, data)				Sends a message through the WebSocket. @param {string} event - the event name. @param {Object} data - The payload to send
 */

class WebSocketService
{
	static instance;
	constructor()
	{
		this.ws = null;
		this.eventHandlers = new Map();
		this.url = null;
		this.reconnectAttempts = 0;
		this.maxReconnectAttempts = 5;
		this.reconnectDelay = 3000;
		this.isReconnecting = false;
		this.shouldReconnect = true;
	}
	static getInstance()
	{
		if (!WebSocketService.instance)
				WebSocketService.instance = new WebSocketService();
		return WebSocketService.instance;
	}
	connect(url)
	{
		if (this.ws && this.ws.readyState === WebSocket.OPEN)
			{
			console.warn("WebScoket already connected. Skipping reconnection.");
			return;
		}
		this.url = url;
		this.ws = new WebSocket(url);
		this.ws.onopen = () => {
			console.log("WebSocket connection established!");
			this.reconnectAttempts = 0;
			this.isReconnecting = false;
			//Notify server that this is a reconnection
			const playerId = localStorage.getItem('player_id');
			const roomId = localStorage.getItem('roomId');
			if (playerId && roomId) {
				console.log("Sending reconnection event...");
				this.send("reconnect", { player_id: playerId, room_id: roomId });
			}
		};

		this.ws.onmessage = (event) => {
			const message = JSON.parse(event.data);
			const eventType = typeof message.event === "string" ? message.event : message.event.event;
			const handlers = this.eventHandlers.get(eventType) || [];
			if (eventType === "player_reconnected" && this.isReconnecting) {
				return;
			}
			handlers.forEach((handler) => handler(message));
		};

		this.ws.onclose = (event) => {
			if (!this.shouldReconnect) {
				console.warn("WebSocket closed intentionally, no reconnection.");
				return;
			}
			console.warn("WebSocket connection lost. Attempting to reconnect...");
			if (!this.isReconnecting) {
				this.isReconnecting = true;
				this.reconnect();
			}
		};
		this.ws.onerror = (error) => { console.error("WebSocket error:", error); };
	}
	reconnect()
	{
		if (this.reconnectAttempts >= this.maxReconnectAttempts)
		{
			console.error("Max reconnection attempts reached. Stopping.");
			return;
		}
		this.reconnectAttempts++;
		console.log(`Reconnection attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts}...`);
		setTimeout(() => {
			console.log("Reconnecting WebSocket...");
			this.connect(this.ws.url);
		}, this.reconnectDelay);
	}
	isConnected()
	{
		return this.ws && this.ws.readyState === WebSocket.OPEN;
	}
	disconnect()
	{
		console.log("WebSocketService: Disconnecting...");
		this.shouldReconnect = false;
		if (this.ws)
		{
			this.ws.close();
			this.ws = null;
		}
	}
	registerEvent(event, handler)
	{
		if (!this.eventHandlers.has(event))
			this.eventHandlers.set(event, []);
		console.log(`Registering event: ${event}`);
		this.eventHandlers.get(event).push(handler);
	}
	unregisterEvent(event, handler)
	{
		if (this.eventHandlers.has(event))
		{
			const handlers = this.eventHandlers.get(event).filter(h => h !== handler);
			this.eventHandlers.set(event, handlers);
		}
	}
	send(event, data)
	{
		if (this.ws && this.ws.readyState === WebSocket.OPEN)
			this.ws.send(JSON.stringify({ event, ...data }));
		else
			console.error("WebSocket is not connected.");
	}
}

//export default WebSocketService;
window.WebSocketService = WebSocketService;