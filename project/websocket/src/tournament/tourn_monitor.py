import json
import asyncio
import aiohttp

from ..network.room_manager import register_player, unregister_player, connected_players
from ..network.redis_utils import broadcast_to_room, notify_players
from ..config import logger
from ..game.game_manager import game_manager
from ..game.player_manager import eliminate_player
from .pong.views.py import update_matches

def TournNextMatch(room):

def TournMonitor(room):
    #await update_matches(roomid)
    async with aiohttp.ClientSession() as session:
		async with session.post("http://nginx/api/pong/update_matches/", json=match_data) as response:
			response_text = await response.text()
			logger.info(f"update matches response: {response.status} - {response_text}")
    if False:
        
    return