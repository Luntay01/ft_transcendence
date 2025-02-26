import os
import json
import redis
import logging

# Redis and other configuration constants.
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MAX_PLAYERS_PER_ROOM = 4
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
SETTINGS_FILE = os.getenv("CONFIG_PATH", "/config/settings.json")

DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

"""		Loads the game settings from the JSON file into a Python dictionary. """
def load_game_settings():

	try:
		with open(SETTINGS_FILE, "r") as file:
			settings = json.load(file)
			return settings
	except FileNotFoundError:
		print(f"Error: settings.json file not found at {SETTINGS_FILE}!")
	except json.JSONDecodeError as e:
		print(f"Error: Invalid JSON format in {SETTINGS_FILE}! {e}")
	return {}

GAME_SETTINGS = load_game_settings()

"""		Redis Channels for Event Handling
This dictionary stores different types of Redis pub/sub channels used by the server.
Adding a new event?
- If the event requires real-time updates to players, add it under `"game_events"`.
- If new categories of events (e.g., `"chat_events"`, `"admin_events"`) are needed create a new key-value pair in this dictionary.
"""
REDIS_CHANNELS = {
	"game_events": [
		"start_game",
		"update_position",
		"ball_update",
		"ball_updates",
		"ball_spawn",
		"start_game_countdown",
		"ball_despawn",
		"player_eliminated",
		"game_over"
	]
}

# Logging Configuration
log_level = GAME_SETTINGS.get("logging", {}).get("level", DEFAULT_LOG_LEVEL).upper()
log_format = GAME_SETTINGS.get("logging", {}).get("format", DEFAULT_LOG_FORMAT)
logging.basicConfig(level=getattr(logging, log_level, logging.DEBUG), format=log_format)

# Main application logger.
logger = logging.getLogger("websocket")
logger.info("Logging initialized with level: %s", log_level)
logger.info("Successfully loaded game settings!")

# Adjust logging for external modules:
# This will suppress DEBUG-level messages from the websockets.server module.
logging.getLogger("websockets.server").setLevel(logging.INFO)

# Create a separate logger for update loops.
# By default, its level is set to WARNING so that debug logs in update loops are hidden.
update_logger = logging.getLogger("websocket.update")
update_logger.setLevel(logging.WARNING)