from django.urls import path
from .views import matchmaking

urlpatterns = [
	path('matchmaking/', matchmaking, name='matchmaking'),
]