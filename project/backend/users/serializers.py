from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'username']

    # override to hash password
    def create(self, validated_data):
        unhashed_password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if unhashed_password is not None:
            instance.set_password(unhashed_password)
        instance.save()
        return instance

class OauthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'date_joined']