from django.urls import path
from .views import matchmaking, room_status

urlpatterns = [
	path('matchmaking/', matchmaking, name='matchmaking'),
	path('rooms/<int:room_id>/', room_status, name='room_status'),
]