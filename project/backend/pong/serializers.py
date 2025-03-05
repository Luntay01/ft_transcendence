from rest_framework import serializers
from .models.match import MatchResult
from users.models import User

class MatchResultSerializer(serializers.ModelSerializer):
	winner = serializers.StringRelatedField()
	players = serializers.StringRelatedField(many=True)
	elimination_order = serializers.JSONField()
	class Meta:
		model = MatchResult
		fields = ['id', 'room', 'winner', 'players', 'elimination_order', 'start_time', 'end_time']

