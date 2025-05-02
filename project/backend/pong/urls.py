from django.urls import path
from .views import matchmaking, room_status, get_match_results, submit_match_result, update_matches, tournpage_response, leave_matchmaking

urlpatterns = [
	path('matchmaking/', matchmaking, name='matchmaking'),
	path('rooms/<int:room_id>/', room_status, name='room_status'),
	path("match_results/winner/<int:winner_id>/", get_match_results, name="get_match_results"),
	path("match_results/", submit_match_result, name="submit_match_result"),
	path('update_matches/', update_matches, name='update_matches'),
	path('tournpage_response/', tournpage_response, name='tournpage_response'),
	path('leave_matchmaking/', leave_matchmaking, name='leave_matchmaking'),
]