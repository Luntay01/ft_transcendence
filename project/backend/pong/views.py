import json
import redis
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now,  make_aware
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Room
from .models.match import MatchResult
from users.models import User
from django.http import JsonResponse
from .models import MatchResult
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from dateutil import parser

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
	game_mode = request.POST.get('gameMode', '4-player')
	if not player_id:
		logger.error("Missing player_id in request")
		return HttpResponseBadRequest("player_id is required")
	try:
		player = User.objects.get(id=player_id)
	except User.DoesNotExist:
		logger.error(f"User with ID {player_id} does not exist")
		return JsonResponse({"error": "User does not exist"}, status=404)
	max_players = 2 if game_mode == "2-player" else 4
	room = Room.objects.available_rooms(max_players).first()
	if not room:
		room = Room.objects.create_room(max_players=max_players)
	logger.info(f"Player {player.username} (ID: {player.id}) is joining Room {room.id}")
	room.add_player(player)
	#logger.info(f"Added player {player.username} (ID: {player.id}) to Room {room.id}")
	redis_client.publish("player_joined", json.dumps({ "event": "player_joined", "room_id": room.id, "player_id": player.id, "player_username": player.username,}))
	#logger.info(f"Published player_joined event for Player {player.id} in Room {room.id}")
	if room.is_full:
		goal_zones = ["bottom", "top"] if game_mode == "2-player" else ["bottom", "top", "left", "right"]
		players_with_goals = []
		for idx, player in enumerate(room.players.all()):
			players_with_goals.append({
				"player_id": player.id,
				"username": player.username,
				"goal_zone": goal_zones[idx]  # explicitly assign goal zones here
			})
		start_game_payload = {
			"event": "start_game",
			"room_id": room.id, 
			"players": players_with_goals,
			"gameMode": game_mode,
		}
		redis_client.publish("start_game", json.dumps(start_game_payload))

	response_payload = {
		'room_id': room.id,
		'is_full': room.is_full,
		'players': [{"player_id": p.id, "username": p.username} for p in room.players.all()],
		'gameMode': game_mode,
	}
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

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_match_result(request):
	if request.method != "POST":
		return Response({"error": "Metod Not Allowed Use POST instead."}, status=405)
	data = request.data
	room_id = data.get("room_id")
	winner_id = data.get("winner_id")
	player_results = data.get("players")
	elimination_order = data.get("elimination_order", [])
	if isinstance(elimination_order, str):
		try:
			elimination_order = json.loads(elimination_order)
		except json.JSONDecodeError:
			return Response({"error": "Invalid elimination_order format"}, status=400)
	if not room_id or not winner_id or not player_results:
		return Response({"error": "Missing required data"}, status=400)
	try:
		room = Room.objects.get(id=room_id)
		winner = User.objects.get(id=winner_id)
	except (Room.DoesNotExist, User.DoesNotExist):
		return Response({"error": "Invalid room or winner"}, status=400)
	match = MatchResult.objects.create(
		room=room,
		winner=winner,
		start_time=make_aware(parser.parse(data.get("start_time", now().isoformat()))),
		end_time=now(),
		elimination_order=elimination_order
	)
	placement_rewards = [50, 20, 0, -10]
	for index, player_id in enumerate(reversed(elimination_order)):
		try:
			player = User.objects.get(id=player_id)
			match.players.add(player)
			change = placement_rewards[min(index, len(placement_rewards) - 1)]
			player.trophies = max(0, player.trophies + change)
			player.save()
			logger.info(f"Updated {player.username}'s trophies by {change}. New total: {player.trophies}")
		except User.DoesNotExist:
			return Response({"error": f"Player {player_id} does not exist"}, status=400)
	match.save()
	return Response({"message": "Match result stored successfully", "match_id": match.id}, status=201)

@api_view(['GET'])
def get_match_results(request, winner_id):
	try:
		match = MatchResult.objects.filter(winner__id=winner_id).order_by('-end_time').first()
		if not match:
			return JsonResponse({"error": "no match found for this player"}, status=404)
		players = match.players.all().values("id", "username", "trophies")
		response_data = {
			"room_id": match.room.id,
			"winner": {
				"id": match.winner.id,
				"username": match.winner.username,
				"trophies": match.winner.trophies,
			},
			"players": list(players),
			"elimination_order": match.elimination_order,
		}
		return JsonResponse(response_data, safe=False)
	except MatchResult.DoesNotExist:
		return JsonResponse({"error": "Match not found"}, status=404)