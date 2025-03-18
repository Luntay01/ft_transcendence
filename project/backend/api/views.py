from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, JsonResponse


def ping(request):
    return JsonResponse({"message": "pong"})

from .serializers import OauthCodeSerializer
from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .otp import generate_otp, verify_otp
from .gmail_service import get_gmail_service, send_email
from .utils import get_tokens_for_user, get_image_b64, get_auth_url

from users.models import User
from users.serializers import UserSerializer
from users.views import UserView
import requests
import logging
import os

class CodeVerifyView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request, fromat=None):
        user = User.objects.get(email=request.data['email'], provider='Pong')
        verify_code = request.data['verify_code']
        if verify_otp(user, verify_code):
            user.is_verified = True
            user.save()
            tokens = get_tokens_for_user(user)
            return Response(tokens, status.HTTP_200_OK)
        return Response({'error': 'Invalid OTP'}, status.HTTP_401_UNAUTHORIZED)

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
            message = f'This is one-time password for login.\nVerify it within 5 minutes.\n\n{verify_code}'
            send_email(service, user.get().email, subject, message)
            return Response({'message': 'Email has been sent' }, status.HTTP_200_OK)
        elif user.get().mfa == 'Authenticator':
            image = get_image_b64(get_auth_url(user.get()))
            return Response({'message': 'QRCode is generated', 'image': image}, status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid MFA method is set'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignupView(views.APIView):
    permission_classes = [AllowAny]
    def verify_email(self, address):
        service = get_gmail_service()
        subject = "Verify Email"
        user = User.objects.get(email=address, provider='Pong')
        message = f'This is one-time password for signup.\nPlease verify it within 5 minutes.\n\n{generate_otp(user)}'
        send_email(service, address, subject, message)
        return
    
    def post(self, request, format=None):
        UserView().post(request)
        self.verify_email(request.data['email'])
        return Response({'message': 'Verification email has been sent'}, status.HTTP_201_CREATED)

class ProfileView(views.APIView):
    def patch(self, request, format=None):
        if 'mfa' in request.data:
            user = request.user
            if request.data['mfa'] == 'Email':
                verify_code = generate_otp(user)
                service = get_gmail_service()
                subject = "Verify Email"
                message = f'This is one-time password for setting MFA option.\nVerify it within 5 minutes.\n\n{verify_code}'
                send_email(service, user.email, subject, message)
                return Response({'message': 'Email has been sent' }, status.HTTP_200_OK)
            elif request.data['mfa'] == 'Authenticator':
                image = get_image_b64(get_auth_url(user))
                return Response({'message': 'QRCode is generated', 'image': image}, status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid MFA method is set'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        user = UserView().patch(request)
        if user.status_code != 200:
            return Response({'error': 'Failed to update user'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        tokens = get_tokens_for_user(User.objects.get(id=user.data['id']))
        return Response(tokens, status=status.HTTP_200_OK)

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
