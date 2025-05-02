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
	game_type = request.POST.get('game_type')
	if not player_id:
		logger.error("Missing player_id in request")
		return HttpResponseBadRequest("player_id is required")
	if not game_type:
		logger.error("Missing game_type in request")
		return HttpResponseBadRequest("game_type is required")
	try:
		game_type = int(game_type)
		if not (0 <= game_type < 4):
			raise ValueError("game_type out of range")
	except ValueError:
		logger.error("game_type {game_type} is not a valid game type (not numeric or outside)")
		return HttpResponseBadRequest("game_type is required to be numeric")
	try:
		player = User.objects.get(id=player_id)
	except User.DoesNotExist:
		logger.error(f"User with ID {player_id} does not exist")
		return JsonResponse({"error": "User does not exist"}, status=404)
	# create a new room with the specified game_type
	room = None
	max_players = 2 if game_mode == "2-player" else 4
	for next in Room.objects.available_rooms(max_players):
		if next.game_type == game_type:
			room = next
			break
	if room is None:
		room = Room.objects.create_room(max_players=max_players)
		room.update_game_type(game_type)
	#max_players = 2 if game_mode == "2-player" else 4
	#room = Room.objects.available_rooms(max_players).first()
	#if not room or not (game_type == room.game_type):
	#	room = Room.objects.create_room(max_players=max_players)
	#	room.update_game_type(game_type)

	logger.info(f"Player {player.username} (ID: {player.id}) is joining Room {room.id}")
	room.add_player(player)
	#logger.info(f"Added player {player.username} (ID: {player.id}) to Room {room.id}")
	redis_client.publish("player_joined", json.dumps({ "event": "player_joined", "room_id": room.id, "player_id": player.id, "player_username": player.username,}))
	#logger.info(f"Published player_joined event for Player {player.id} in Room {room.id}")
	#logger.debug(f"Player connected to room: {room.id} on game_type: {room.game_type} max_players: {room.max_players} is_full: {room.is_full}")
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
			"game_type" : game_type,
		}
		redis_client.publish("start_game", json.dumps(start_game_payload))

	response_payload = {
		'room_id': room.id,
		'is_full': room.is_full,
		'players': [{"player_id": p.id, "username": p.username} for p in room.players.all()],
		'gameMode': game_mode,
		'game_type': game_type,
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
	room, created = Room.objects.get_or_create(id=room_id)
	if created:
		logger.warning(f" Room {room_id} was recreated to allow match result storage.")
	try:
		winner = User.objects.get(id=winner_id)
	except User.DoesNotExist:
		logger.error(f"Error: Winner {winner_id} does not exist")
		return Response({"error": f"Invalid winner {winner_id}"}, status=400)
	logger.info(f"Winner: {winner.username}")
	logger.info(f"Room ID: {room.id}")
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

@csrf_exempt
def tournpage_response(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Invalid request method")
	signal = 0
	signal = int(request.POST.get('signal', 0))
	room_id = request.POST.get('room_id', 0)
	
	if signal is None:
		return HttpResponseBadRequest("signal not found to send")
	signal_data = {
		"event": "tourn_signal",
		"room_id": room_id,
		"signal": signal,
    }
	redis_client.publish("update_matches", json.dumps(signal_data))
	return JsonResponse({"message": f"tourn signal page swap sent"})


@csrf_exempt
def update_matches(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Invalid request method")
	matches = request.POST.get('matches')
	room_id = request.POST.get('room_id')
	#matches number err check
	#room_id = int(room_id)
	#room = Room.objects.filter(id=room_id).first()
	#room = None
	room, created = Room.objects.get_or_create(id=room_id)
	if created:
		logger.warning(f" Room {room_id} was recreated to allow match result storage.")
	#for next in Room.objects.full_rooms():
	#	logger.info(f"room_id: {room_id}")
	#	logger.info(f"Room dot ID: {next.id}")
	#	if next.id == room_id:
	#		room = next
	#		break
	if room is None:
		return HttpResponseBadRequest("Room id not found to decrement matches")
	room.decrement_matches(matches)
	room_payload = {
		"event": "update_matches",
		"room_id": room.id, 
		"matches": room.matches_left,
		"room_done": room.room_done,
	}
	#send off updates to a monitor waiting
	#if room.room_done == True:
	redis_client.publish("update_matches", json.dumps(room_payload))
	return JsonResponse({"message": f"matches updated successfully"})


@csrf_exempt
def leave_matchmaking(request):
	if request.method != "POST":
		return JsonResponse({"error": "Invalid request method"}, status=405)
	import json
	data = json.loads(request.body.decode("utf-8"))
	player_id = data.get("player_id")
	if not player_id:
		return JsonResponse({"error": "Player ID is required"}, status=400)
	try:
		player = User.objects.get(id=player_id)
	except User.DoesNotExist:
		return JsonResponse({"error": "User not found"}, status=404)
	room = Room.objects.filter(players=player).first()
	if not room:
		return JsonResponse({"error": "Player is not in a matchmaking room"}, status=404)
	room.remove_player(player)
	room.save()
	#clear room function from kyle not used here, pretty sure delete doesnt work or at least doesnt clear variables
	if room.players.count() == 0:
		#room.clear_room()
		room.delete()
	return JsonResponse({"message": f"Player {player_id} removed from matchmaking"})