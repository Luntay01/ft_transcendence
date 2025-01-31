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