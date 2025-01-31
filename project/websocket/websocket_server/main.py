import asyncio
import websockets
import json
from .handler import handler
from .redis_utils import redis_client, notify_players
from .logger import logger

"""
WebSocket Server Architecture
========================================
This script manages WebSocket connections, Redis message handling, and game state synchronization.
It acts as a bridge between players by ensuring real-time communication through WebSockets.

1. **Matchmaking and room assignment**
   - players request matchmaking via `/api/pong/matchmaking/`
   - the matchmaking API assigns them to a room or creates a new one
   - player information is stored in Redis and a `player_joined` event is published
   - once a room is full, a `start_game` event is triggered

2. **Websocket connections**
   - when a player joins a game, they connect via WebSockets using their `room_id` and `player_id`
   - the `handler` function processes WebSocket messages and routes them accordingly.
   - messages are broadcasted to all players in the room via `broadcast_to_room`

3. **redis integration for game events**
   - redis acts as a message broker for real-time updates
   - `redis_listener()` listens for events such as `start_game` and `update_position`
   - when a new event is received, it is forwarded to connected players via WebSockets

4. **handling player actions (movement, score updates, etc.)*
   - players send movement updates via WebSockets (`player_move`)
   - the server distirbutes these updates to all clients in the room
   - movement is validated and synchronized across players

## file references:
- `frontend/src/js/WebSocketService.js` - manages WebSocket connections on the client side
- `frontend/src/js/games/gamePong/js/utils/GameWebSocketHandlers.js` - processes incoming websocket messages
- `frontend/src/js/games/gamePong/js/utils/PlayerInput.js` - sends player input data to the server

## key functions in main.py:
- `handler(websocket, path)`: manages websocket connections per player
- `redis_listener()`: listens for game events from redis and forwards them to Websocket clients
- `notify_players(room_id, message)`: Sends messages to all players in a room
- `broadcast_to_room(room_id, message, exclude=None)`: broadcatss a message to all players except the sender
- `register_player(websocket, room_id, player_id, username)`: registers a player to the room and informs others
- `unregister_player(websocket, room_id, player_id)`: handles player disconnection cleanup
- `start_game(room_id)`: triggers game start when a room is full

"""


"""
listen to Redis channels and relay messages to players
"""
async def redis_listener():
	pubsub = redis_client.pubsub()
	pubsub.subscribe("start_game", "update_position")
	try:
		while True:
			message = pubsub.get_message(ignore_subscribe_messages=True)
			if message and message["type"] == "message":
				data = json.loads(message["data"])
				logger.debug(f"Redis message received: {data}")
				room_id = data.get("room_id")
				if room_id:
					await notify_players(room_id, data)
			await asyncio.sleep(0.1)  # Prevent high CPU usage
	except Exception as e:
		logger.error(f"Redis listener error: {e}")


"""
main entry point to start the WebSocket server and Redis listener
"""
async def main():
	logger.info("Starting WebSocket server on ws://0.0.0.0:8765...")
	await asyncio.gather(
		websockets.serve(handler, "0.0.0.0", 8765),
		redis_listener(),
	)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except Exception as e:
		logger.error(f"Critical server error: {e}")


