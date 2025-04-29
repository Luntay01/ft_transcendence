from datetime import datetime
from rest_framework import serializers
from .models import User
from django.core.files.base import ContentFile
from django.conf import settings
import os

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
        picture = validated_data.pop('picture', None)
        if picture is None:
            with open(settings.MEDIA_ROOT.joinpath(settings.DEFAULT_IMAGE_PATH), 'rb') as image_file:
                image_content = image_file.read()
            image = ContentFile(image_content, name=f"{validated_data['username']}_profile.png")
            validated_data['picture'] = image
        unhashed_password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if unhashed_password is not None:
            instance.set_password(unhashed_password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.provider = validated_data.get('provider', instance.provider)
        instance.oauth_user_id = validated_data.get('oauth_user_id', instance.oauth_user_id)
        unhashed_password = validated_data.pop('password', None)
        if unhashed_password is not None:
            instance.set_password(unhashed_password)
        instance.username = validated_data.get('username', instance.username)
        new_picture = validated_data.pop('picture', None)
        if new_picture is not None:
            # Delete the old picture file if it exists
            if instance.picture and os.path.isfile(instance.picture.path) and instance.picture.path != settings.DEFAULT_IMAGE_PATH:
                os.remove(instance.picture.path)
            new_picture_name = f"{instance.username}_profile.png"
            instance.picture.save(new_picture_name, new_picture, save=False)
        instance.otp_secret = validated_data.get('otp_secret', instance.otp_secret)
        instance.is_verified = validated_data.get('is_verified', instance.is_verified)
        instance.mfa = validated_data.get('mfa', instance.mfa)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.trophies = validated_data.get('trophies', instance.trophies)
        instance.birth_day = validated_data.get('birth_day', instance.birth_day)
        instance.save()
        return instance
