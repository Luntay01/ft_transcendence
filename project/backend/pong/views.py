import json
import redis
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Room
from users.models import User

logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

"""
Handle matchmaking for players.
This matchmaking function is responsible for assigning players to available rooms or creating
a new room if none are available it also interacts with Redis to notify the WebSocket
server about player activities such as joining a room or starting a game.
- Accepts a POST request with `player_id`.
- Attempts to place the player in an available room.
- Creates a new room if no available rooms exist.
- Publishes a `player_joined` event to Redis for WebSocket updates.
- If the room becomes full, publishes a `start_game` event to Redis.
Decorators:
	@csrf_exempt: sisables CSRF protection for this endpoint. this is useful for
	APIs where the client might not include a CSRF token.
Args:
	request (httprequest): HTTP request containing `player_id` in the POST body.
Returns:
	JsonResponse: contains room information (room_id, is_full, players) on success.
	returns an error message with appropriate HTTP status code on failure.
"""
@csrf_exempt
def matchmaking(request):
	if request.method != 'POST': return HttpResponseBadRequest("Invalid request method")
	player_id = request.POST.get('player_id')
	if not player_id:
		logger.error("Missing player_id in request")
		return HttpResponseBadRequest("player_id is required")
	try:
		player = User.objects.get(id=player_id)
	except User.DoesNotExist:
		logger.error(f"User with ID {player_id} does not exist")
		return JsonResponse({"error": "User does not exist"}, status=404)
	room = Room.objects.available_rooms().first() or Room.objects.create_room()
	logger.info(f"Player {player.username} (ID: {player.id}) is joining Room {room.id}")
	room.add_player(player)
	logger.info(f"Added player {player.username} (ID: {player.id}) to Room {room.id}")
	redis_client.publish("player_joined", json.dumps({ "event": "player_joined", "room_id": room.id, "player_id": player.id, "player_username": player.username,}))
	logger.info(f"Published player_joined event for Player {player.id} in Room {room.id}")
	if room.is_full:
		logger.info(f"Room {room.id} is now full. Broadcasting start_game event.")
		redis_client.publish("start_game", json.dumps({ "event": "start_game", "room_id": room.id, "players": [player.username for player in room.players.all()], }))
	return JsonResponse({'room_id': room.id, 'is_full': room.is_full, 'players': [player.username for player in room.players.all()],})