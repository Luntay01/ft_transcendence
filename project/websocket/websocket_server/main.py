import asyncio
import websockets
import json
import signal
from .handler import handler
from .redis_utils import redis_client, notify_players, publish_to_redis
from .config import logger
from .game_manager import GameManager
from .room_manager import connected_players

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
- `register_player(websocket, room_id, player_id, username, gameMode)`: registers a player to the room and informs others
- `unregister_player(websocket, room_id, player_id, gameMode)`: handles player disconnection cleanup
- `start_game(room_id)`: triggers game start when a room is full

"""
game_manager = GameManager()

async def ensure_all_players_connected(room_id, expected_players_data):
	expected_player_ids = {str(player["player_id"]) for player in expected_players_data}
	logger.info(f"Waiting for players {expected_player_ids} to connect to Room {room_id}...")
	while True:
		connected_player_ids = {player["player_id"] for player in connected_players.get(room_id, [])}
		# Check if all expected players are connected
		if expected_player_ids.issubset(connected_player_ids):
			logger.info(f"All players connected to Room {room_id}: {connected_player_ids}")
			break
		await asyncio.sleep(0.1)  # Check every 100ms

async def handle_event(event, room_id, data):
	if event == "start_game":
		await ensure_all_players_connected(room_id, data["players"])
		players = connected_players.get(room_id, [])
		game_manager.create_game(room_id, players)
		game_manager.start_game(room_id)
		logger.info(f"game started for Room {room_id}")
	# add more costom event handling if needed in the future
	# elif event == "score_update":
	#	 handle_score_update(room_id, data)

async def redis_listener():
	pubsub = redis_client.pubsub()
	pubsub.subscribe("start_game", "update_position", "ball_update", "ball_spawn", "start_game_countdown")
	while True:
		message = pubsub.get_message(ignore_subscribe_messages=True)
		if message and message["type"] == "message":
			data = json.loads(message["data"])
			room_id = str(data.get("room_id"))
			event = data.get("event")
			await handle_event(event, room_id, data)
			await notify_players(room_id, data)
		await asyncio.sleep(0.016)  # prevent high CPU usage

async def game_update_loop():
	while True:
		game_manager.update_games(delta_time=0.016)
		await asyncio.sleep(0.016)

async def main():
	logger.info("Starting WebSocket server...")
	stop_event = asyncio.Event()
	# Shutdown handler
	def shutdown():
		logger.info("Shutdown signal received. Cleaning up...")
		stop_event.set()
	# Handle SIGTERM and SIGINT
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGTERM, shutdown)
	loop.add_signal_handler(signal.SIGINT, shutdown)
	try:
		server = await websockets.serve(handler, "0.0.0.0", 8765)
		await asyncio.gather(
			redis_listener(),
			game_update_loop(),
			stop_event.wait()  # Wait until shutdown signal is received
		)
	finally:
		logger.info("WebSocket server shutting down...")
		server.close()
		await server.wait_closed()
		logger.info("WebSocket server has stopped.")

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except Exception as e:
		logger.error(f"Critical server error: {e}")













"""
# Store ball managers per room
ball_managers = {}


async def start_game(room_id):
	#players = [f"Player{index + 1}" for index in range(MAX_PLAYERS_PER_ROOM)]

	if room_id not in ball_managers:
		ball_managers[room_id] = BallManager(room_id)
		ball_managers[room_id].spawn_ball()
	else:
		logger.warning(f"start_game called for {room_id}, but BallManager already exists.")

	start_game_event = {
		"event": "start_game",
		"room_id": room_id,
		"players": [
			{"player_id": player["player_id"], "username": player["username"]}
			for player in connected_players.get(room_id, [])
		]
	}
	await publish_to_redis("start_game", start_game_event)
	logger.info(f"Room {room_id} is now full. Game started.")


async def redis_listener():
	pubsub = redis_client.pubsub()
	pubsub.subscribe("start_game", "update_position", "ball_update", "ball_spawn")
	logger.debug("📡 Subscribed to Redis channels: start_game, update_position, ball_update, ball_spawn")
	try:
		while True:
			message = pubsub.get_message(ignore_subscribe_messages=True)
			if message and message["type"] == "message":
				data = json.loads(message["data"])
				logger.debug(f"Redis message received: {data}")

				room_id = str(data.get("room_id"))
				event = data.get("event")
				# Handle start_game
				if event == "start_game":
					if room_id not in ball_managers:
						ball_managers[room_id] = BallManager(room_id)
						ball_managers[room_id].game_active = True
						logger.debug(f"🏀 BallManager created for room {room_id}")
					await notify_players(room_id, data)
				# Handle ball_spawn
				elif event == "ball_spawn":
					if room_id in ball_managers:
						ball_managers[room_id].balls.append({
							"id": data["ball_id"],
							"position": data["position"],
							"velocity": data["velocity"]
						})
						logger.debug(f"⚽ Ball {data['ball_id']} added to room {room_id}")
					await notify_players(room_id, data)
				elif event == "ball_update":
					logger.debug(f"🔄 Ignoring ball_update event in redis_listener (handled by ball_update_loop)")
				elif event == "update_position":
					await notify_players(room_id, data)
				else:
					logger.warning(f"Unhandled event type: {event}")
			await asyncio.sleep(0.016)  # Prevent high CPU usage
	except Exception as e:
		logger.error(f"Redis listener error: {e}")



async def ball_update_loop():
	logger.info("⚙️ Ball update loop is running. Waiting for games to start...")

	while True:
		for room_id, manager in ball_managers.items():
			if getattr(manager, 'game_active', False):  # Check if the game is active
				logger.debug(f"🚀 Updating balls for active game in Room {room_id}.")
				manager.update_balls(delta_time=0.016)
			else:
				logger.debug(f"⏸️ Game not active for Room {room_id}. Skipping ball updates.")

		await asyncio.sleep(0.016)  # 60 FPS update rate


async def main():
	logger.info("Starting WebSocket server on ws://0.0.0.0:8765...")
	await asyncio.gather(
		websockets.serve(handler, "0.0.0.0", 8765),
		redis_listener(),
		ball_update_loop(),
	)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except Exception as e:
		logger.error(f"Critical server error: {e}")
"""

