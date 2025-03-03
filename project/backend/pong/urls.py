from django.urls import path
from .views import matchmaking, room_status, get_match_results, submit_match_result

urlpatterns = [
	path('matchmaking/', matchmaking, name='matchmaking'),
	path('rooms/<int:room_id>/', room_status, name='room_status'),
	path("match_results/winner/<int:winner_id>/", get_match_results, name="get_match_results"),
	path("match_results/", submit_match_result, name="submit_match_result"),
]