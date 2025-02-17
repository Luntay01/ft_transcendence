from rest_framework import serializers
from .models import Game

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'id', 'player', 'score', 'match_start', 'match_end', 
            ]


# class UserGamesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Game
#         fields = [
#             'id', 'player', 'score', 'match_start', 'match_end', 
#             ]
