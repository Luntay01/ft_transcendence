from rest_framework import serializers
from django.contrib.auth.models import User as Usr
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']