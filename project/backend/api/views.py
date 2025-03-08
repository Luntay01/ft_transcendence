from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, JsonResponse


def ping(request):
    return JsonResponse({"message": "pong"})

from .serializers import OauthCodeSerializer
from rest_framework import views, status
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt import exceptions as jwt_exp
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserSerializer
import requests
import logging
import os

class OauthCodeView(views.APIView):
    permission_classes = [AllowAny]
    #TODO: remove logging (import as well)
    def post(self, request):
        CLIENT_ID = os.environ.get('CLIENT_ID')
        CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
        HOST_URI = os.environ.get('HOST_PROTOCOL') + '://' + os.environ.get('HOST_DOMAIN') + ':' + os.environ.get('HOST_PORT')
        serializer = OauthCodeSerializer(data=request.data)
        if not (serializer.is_valid()):
            return Response(status.HTTP_422_UNPROCESSABLE_ENTITY)
        code = serializer.validated_data['code']
        logging.warning('code: ' + code)    #debug
        state = serializer.validated_data['state']
        logging.warning('state: ' + state)    #debug
        post_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': HOST_URI + '/callback', 
            'state': state,
            }
        response = requests.post("https://api.intra.42.fr/oauth/token/", data=post_data)

        access_token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        content = response.json()
        # logging.warning('id: ' + str(content["id"]))    #debug
        # logging.warning('username: ' + content["login"])    #debug
        # logging.warning('email: ' + content["email"])    #debug

        queryset = User.objects.filter(oauth_user_id=content["id"])
        if (queryset):
            data = { 'password': access_token, }
            query = User.objects.get(provider='42Oauth', oauth_user_id=content['id'])
            instance = UserSerializer(instance=query, data=data, partial=True)
            if not (instance.is_valid()):
                logging.warning("access token in password field is not valid")
            instance.save()
        else:
            data = {
                'email': content['email'],
                'provider': '42Oauth',
                'oauth_user_id': content['id'],
                'password': access_token,
                'username': content['login'],
            }
            userializer = UserSerializer(data=data, partial=True)
            if not (userializer.is_valid()):
                logging.warning("input is not valid")
            userializer.save()

        # return jwt token
        post_data = {
            'provider': '42Oauth',
            'oauth_user_id': content['id'],
            'password': access_token,
        }
        # The following must be localhost:8000/api/token/ (trailing slash important), as we want the backend to communicate directly with it self
        response = requests.post("http://localhost:8000/api/token/", data=post_data)
        return Response(response.json(), status.HTTP_200_OK)
    
class TokenObtainPairView(jwt_views.TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        if not ('provider' in request.data.keys()):
            return Response({'error': 'Auth provider is not provided'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        provider = request.data['provider']

        if (provider == 'Pong'):
            user = User.objects.filter(email=request.data['email'], provider=provider)
        elif (provider == '42Oauth'):
            user = User.objects.filter(oauth_user_id=request.data['oauth_user_id'], provider=provider)
        else:
            return Response({'error': 'Auth provider is invalid'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if (user.count() != 1):
            return Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        _mutable = data._mutable
        data._mutable = True
        data['id'] = user.get().id
        data._mutable = _mutable
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except jwt_exp.TokenError as e:
            raise jwt_exp.InvalidToken(e.args[0])
        
         # including the user ID in the response
        token_response = serializer.validated_data
        user_instance = user.get()
        token_response['id'] = user_instance.id  # Add the user ID
        token_response['username'] = user_instance.username  # Add the username

        return Response(token_response, status=status.HTTP_200_OK)