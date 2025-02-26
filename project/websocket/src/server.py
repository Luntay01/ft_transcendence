import asyncio
import websockets
import signal

from .network.websocket_handler import handler as websocket_handler
from .network.redis_listener import start_redis_listener
from .game.game_loop import start_game_update_loop
from .config import logger

"""
WebSocket Server
-----------------
Entry point for the WebSocket server, responsible for:
  - Managing WebSocket connections.
  - Listening for Redis game events.
  - Running game updates.
For a detailed architecture overview, see `docs/server_architecture.md`.
"""

"""Initialize and start the WebSocket server."""
async def start_server():
	logger.info("Starting WebSocket server...")
	stop_event = asyncio.Event()

	def shutdown():
		logger.info("Shutdown signal received. Cleaning up...")
		stop_event.set()

	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGTERM, shutdown)
	loop.add_signal_handler(signal.SIGINT, shutdown)

	server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
	try:
		await asyncio.gather(
			start_redis_listener(),
			start_game_update_loop(),
			stop_event.wait()
		)
	finally:
		logger.info("WebSocket server shutting down...")
		server.close()
		await server.wait_closed()
		logger.info("WebSocket server has stopped.")

if __name__ == "__main__":
	try:
		asyncio.run(start_server())
	except Exception as e:
		logger.error(f"Critical server error: {e}")

















""""import asyncio
import websockets
import json
import signal

from .network.websocket_handler import handler as websocket_handler
from .network.redis_utils import redis_client, notify_players, publish_to_redis
from .config import logger
from .game.game_manager import GameManager
from .network.room_manager import connected_players
"""
"""			ensure_all_players_connected(room_id, expected_players_data):
	Wait until all expected players are connected to the specified room.
	Args:
		room_id (str): The room identifier.
		expected_players_data (list): List of player data dictionaries expected in the room.

game_manager = GameManager()

async def	ensure_all_players_connected(room_id, expected_players_data):
	expected_player_ids = {str(player["player_id"]) for player in expected_players_data}
	logger.info(f"Waiting for players {expected_player_ids} to connect to Room {room_id}...")
	while True:
		connected_player_ids = {player["player_id"] for player in connected_players.get(room_id, [])}
		if expected_player_ids.issubset(connected_player_ids):
			logger.info(f"All players connected to Room {room_id}: {connected_player_ids}")
			break
		await asyncio.sleep(0.1)
"""
"""			handle_event(event, room_id, data):
	Process a game event received from Redis.
	Args:
		event (str): The event type (e.g., "start_game").
		room_id (str): The room identifier.
		data (dict): The event data payload.
	add more costom event handling if needed in the future

async def	handle_event(event, room_id, data):
	if event == "start_game":
		await ensure_all_players_connected(room_id, data["players"])
		players = connected_players.get(room_id, [])
		game_manager.create_game(room_id, players)
		game_manager.start_game(room_id)
		logger.info(f"game started for Room {room_id}")
"""
"""			redis_listener():
	Listen for game-related events on Redis and dispatch them.
	This function subscribes to multiple channels and forwards any received
	messages to the corresponding game event handler and connected WebSocket clients.

async def	redis_listener():
	pubsub = redis_client.pubsub()
	pubsub.subscribe("start_game", "update_position", "ball_update", "ball_spawn", "start_game_countdown", "ball_despawn", "player_eliminated", "game_over")
	while True:
		message = pubsub.get_message(ignore_subscribe_messages=True)
		if message and message["type"] == "message":
			data = json.loads(message["data"])
			room_id = str(data.get("room_id"))
			event = data.get("event")
			await handle_event(event, room_id, data)
			await notify_players(room_id, data)
		await asyncio.sleep(0.016)  # prevent high CPU usage
"""
"""			game_update_loop():
	Continuously update game states.
	This loop calls the game manager's update function at a fixed interval.

async def	game_update_loop():
	while True:
		game_manager.update_games(delta_time=0.016)
		await asyncio.sleep(0.016)
"""
"""			main()
	Start the WebSocket server and associated tasks until a shutdown signal is received.
	This includes setting up signal handlers for graceful shutdown and running the
	Redis listener and game update loops concurrently.
	stop_event.wait()  # Wait until shutdown signal is received
	Handle SIGTERM and SIGINT

async def	main():
	logger.info("Starting WebSocket server...")
	stop_event = asyncio.Event()
	def shutdown():
		logger.info("Shutdown signal received. Cleaning up...")
		stop_event.set()
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGTERM, shutdown)
	loop.add_signal_handler(signal.SIGINT, shutdown)
	try:
		server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
		await asyncio.gather(
			redis_listener(),
			game_update_loop(),
			stop_event.wait()
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