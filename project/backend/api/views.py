from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, JsonResponse


def ping(request):
    return JsonResponse({"message": "pong"})

from .serializers import OauthCodeSerializer
from rest_framework import views, status
from rest_framework_simplejwt import views as jwt_views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from users.otp import generate_otp
from users.gmail_service import get_gmail_service, send_email

from users.models import User
from users.serializers import UserSerializer
import requests
import logging
import os
from .utils import get_tokens_for_user

class OauthCodeView(views.APIView):
    permission_classes = [AllowAny]
    #TODO: remove logging (import as well)
    def post(self, request):
        CLIENT_ID = os.environ.get('CLIENT_ID')
        CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
        
        # Fallback to default port depending on protocol
        # Defaults to https which intern defaults to 443

        HOST_PROTOCOL = os.environ.get('HOST_PROTOCOL', 'https')
        HOST_DEFAULT_PORT = "443" if HOST_PROTOCOL == 'https' else "80"
        HOST_PORT = os.environ.get('HOST_PORT', HOST_DEFAULT_PORT)
        HOST_DOMAIN = os.environ.get('HOST_DOMAIN', 'localhost')
        # Construct the host uri eg this will be used as a return address from OAuth2
        # Don't use domain:port if we're using default ports (42 doesn't like it?) 
        if HOST_PORT == "80" or HOST_PORT == "443": 
            HOST_URI = HOST_PROTOCOL + '://' + HOST_DOMAIN
        else:
            HOST_URI = HOST_PROTOCOL + '://' + HOST_DOMAIN + ':' + HOST_PORT

        serializer = OauthCodeSerializer(data=request.data)
        if not (serializer.is_valid()):
            return Response(status.HTTP_422_UNPROCESSABLE_ENTITY)
        code = serializer.validated_data['code']
        logging.warning('code: ' + code)    #debug
        state = serializer.validated_data['state']
        logging.warning('state: ' + state)    #debug
        REDIRECT_URL = HOST_URI + '/callback'
        post_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URL, 
            'state': state,
            }
        response = requests.post("https://api.intra.42.fr/oauth/token/", data=post_data)
        if response.ok == False:
            logging.error('Unable to Authorise User (OAuth2):' + response.text)
            logging.debug(f'A likely reason why OAuth2 failed is invalid redirect ({REDIRECT_URL}), '
            'perhaps the environment has the wrong HOST_DOMAIN/HOST_PORT/HOST_PROTOCOL configuration, '
            'or the OAuth2 service does not allow the redirection for the specified redirect URL')
            return Response({
                'error': 'oauth_service_error',
                'message': 'The external oauth service failed.',
                'response': response.text
            }, status.HTTP_503_SERVICE_UNAVAILABLE)
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
                'is_verified': True,
            }
            userializer = UserSerializer(data=data, partial=True)
            if not (userializer.is_valid()):
                logging.warning("input is not valid")
            userializer.save()

        # return jwt token
        user = User.objects.get(provider='42Oauth', oauth_user_id=content['id'])
        tokens = get_tokens_for_user(user)
        return Response(tokens, status.HTTP_200_OK)

class LoginView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        if not ('provider' in request.data.keys()):
            return Response({'error': 'Auth provider is not provided'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        provider = request.data['provider']

        if (provider != 'Pong'):
            return Response({'error': 'Auth provider is invalid'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        user = User.objects.filter(email=request.data['email'], provider=provider, is_verified=True)

        if (user.count() != 1):
            return Response({'error': 'User does not exist. Please sign up and verify email.'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.get().mfa == 'Email':
            verify_code = generate_otp(user.get())
            service = get_gmail_service()
            subject = "Verify Email"
            message = f'This is one-time password for login.\nVerify it within 24 hours.\n\n{verify_code}'
            send_email(service, user.get().email, subject, message)
            return Response({'message': 'Email has been sent' }, status=status.HTTP_200_OK)
        elif user.get().mfa == 'Authenticator':
            # TODO: implement authenticator
            return Response({'error': 'Not implemented'}, status.HTTP_501_NOT_IMPLEMENTED)
        else:
            return Response({'error': 'Invalid MFA method is set'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
