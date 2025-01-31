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
		console.log("WebSocketService: New instance created");
	}
	static getInstance()
	{
		if (!WebSocketService.instance)
			{
				console.log("WebSocketService: Creating new instance");
				WebSocketService.instance = new WebSocketService();
			}
			else
			{
				console.log("WebSocketService: Reusing existing instance");
			}
			return WebSocketService.instance;
	}
	connect(url)
	{
		if (this.ws)
		{
			console.warn("WebSocket already connected. Disconnecting and reconnecting...");
			this.disconnect();
		}
		this.ws = new WebSocket(url);
		this.ws.onopen = () => { console.log("WebSocket connection established!"); };
		this.ws.onmessage = (event) => {
			const message = JSON.parse(event.data);
			console.log("Message received:", message);
			const eventType = typeof message.event === "string" ? message.event : message.event.event;
			const handlers = this.eventHandlers.get(eventType) || [];
			console.log(`Found ${handlers.length} handlers for event '${eventType}'`);
			handlers.forEach((handler) => handler(message));
		};
		this.ws.onclose = () => { console.log("WebSocket connection closed."); };
		this.ws.onerror = (error) => { console.error("WebSocket error:", error); };
	}
	disconnect()
	{
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

export default WebSocketService;