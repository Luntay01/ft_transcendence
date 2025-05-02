import os
import json
import redis
import logging

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MAX_PLAYERS_PER_ROOM = 4
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
SETTINGS_FILE = os.getenv("CONFIG_PATH", "/config/settings.json")
DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

"""loads the game settings from the JSON file into a python dictionary."""
def load_game_settings():
	try:
		with open(SETTINGS_FILE, "r") as file:
			settings = json.load(file)
			return settings
	except FileNotFoundError:
		logger.error(f"Error: settings.json file not found at {SETTINGS_FILE}!")
	except json.JSONDecodeError as e:
		logger.error(f"Error: Invalid JSON format in {SETTINGS_FILE}! {e}")
	return {}

GAME_SETTINGS = load_game_settings()

# logging Configuration
log_level = GAME_SETTINGS.get("logging", {}).get("level", DEFAULT_LOG_LEVEL).upper()
log_format = GAME_SETTINGS.get("logging", {}).get("format", DEFAULT_LOG_FORMAT)
logging.basicConfig(level=getattr(logging, log_level, logging.DEBUG), format=log_format)
logger = logging.getLogger("websocket")
logger.info("Logging initialized with level: %s", log_level)
logger.info("Successfully loaded game settings!")