# src/__init__.py
from .config import logger, GAME_SETTINGS
from .server import start_server

__all__ = [
	"logger",
	"GAME_SETTINGS",
	"start_server",
]