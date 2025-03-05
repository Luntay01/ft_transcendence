from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'username', 'picture', 'is_verified', 'mfa',
            'first_name', 'last_name', 'birth_day', 'provider', 'oauth_user_id', 'trophies',
            ]
        extra_kwargs = {
            'id': {
                'read_only': True,
            },
            'password': {
                'write_only': True,
            },
            'picture': {
                'required': False,
            },
            'is_verified': {
                'required': False,
            },
            'mfa': {
                'required': False,
            },
            'first_name': {
                'required': False,
            },
            'last_name': {
                'required': False,
            },
            'birth_day': {
                'required': False,
            },
            'oauth_user_id': {
                'required': False,
            },
            'trophies': {
                'read_only': True},
        }
    
    # override to hash password
    def create(self, validated_data):
        unhashed_password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if unhashed_password is not None:
            instance.set_password(unhashed_password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        unhashed_password = validated_data.pop('password', None)
        if unhashed_password is not None:
            instance.set_password(unhashed_password)
        instance.username = validated_data.get('username', instance.username)
        instance.picture = validated_data.get('picture', instance.picture)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.birth_day = validated_data.get('birth_day', instance.birth_day)
        instance.provider = validated_data.get('provider', instance.provider)
        instance.oauth_user_id = validated_data.get('oauth_user_id', instance.oauth_user_id)
        instance.save()
        return instance

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'date_joined']
