import json
import redis
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
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
	gameMode = request.POST.get('gameMode')
	if not player_id:
		logger.error("Missing player_id in request")
		return HttpResponseBadRequest("player_id is required")
	if not gameMode:
		logger.error("Missing gameMode in request")
		return HttpResponseBadRequest("gameMode is required")
	try:
		player = User.objects.get(id=player_id)
	except User.DoesNotExist:
		logger.error(f"User with ID {player_id} does not exist")
		return JsonResponse({"error": "User does not exist"}, status=404)
	room = Room.objects.available_rooms().first() or Room.objects.create_room()


	logger.info(f"Player {player.username} (ID: {player.id}) is joining Room {room.id}")
	room.add_player(player)
	#logger.info(f"Added player {player.username} (ID: {player.id}) to Room {room.id}")
	redis_client.publish("player_joined", json.dumps({ "event": "player_joined", "room_id": room.id, "player_id": player.id, "player_username": player.username,}))
	#logger.info(f"Published player_joined event for Player {player.id} in Room {room.id}")
	if room.is_full or room.gameMode != gameMode:
		if room.gameMode != gameMode:
			logger.info(f"Room {room.id} does not match the requested gameMode. Creating new room.")
			room.update_gameMode(gameMode)
		start_game_payload = {
			"event": "start_game",
			"room_id": room.id, 
			"players": [{"player_id": player.id, "username": player.username} for player in room.players.all()],
		}
		#logger.debug(f"start_game event payload: {json.dumps(start_game_payload)}")
		redis_client.publish("start_game", json.dumps(start_game_payload))
	response_payload = { 'room_id': room.id, 'is_full': room.is_full, 'players': [{"player_id": player.id, "username": player.username} for player in room.players.all()], }
	#logger.debug(f"Matchmaking API response: {json.dumps(response_payload)}")
	return JsonResponse(response_payload)


@api_view(['GET'])
def room_status(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        data = {
            "room_id": room.id,
            "players": [
                {"player_id": player.id, "username": player.username}
                for player in room.players.all()
            ],
        }
        return Response(data, status=200)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)