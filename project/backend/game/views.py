from django.http import Http404
from rest_framework import views, status
from rest_framework.response import Response
from .serializers import GameSerializer
from .models import Game
from users.models import User

# Create your views here.


class UserGamesView(views.APIView):
    def get_user_object(self, username):
        try:
            return User.objects.get(username=username)
        except Http404:
            raise status.HTTP_404_NOT_FOUND
        
    def get(self, request, username, format=None):
        user = self.get_user_object(username)
        games = Game.objects.all().filter(player=user)
        serializer = GameSerializer(instance=games, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

class GameView(views.APIView):
    def get_object(self, game_id):
        try:
            return Game.objects.get(game_id=game_id)
        except Http404:
            raise status.HTTP_404_NOT_FOUND
        
    def get(self, request, game_id, format=None):
        game = self.get_object(game_id)
        serializer = GameSerializer(instance=game)
        return Response(serializer.data, status.HTTP_200_OK)