from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserSerializer, OauthCodeSerializer
import requests
import logging

class UserRegisterView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not (serializer.is_valid()):
            return Response('', status.HTTP_422_UNPROCESSABLE_ENTITY)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

class OauthCodeView(views.APIView):
    permission_classes = [AllowAny]
    #TODO: define global vars
    #TODO: remove logging (import as well)
    def post(self, request):
        serializer = OauthCodeSerializer(data=request.data)
        if not (serializer.is_valid()):
            return Response(status.HTTP_422_UNPROCESSABLE_ENTITY)
        code = serializer.validated_data['code']
        logging.warning('code: ' + code)    #debug
        client_id = "u-s4t2ud-7eb0d578913ab9934c2b116843901211c2e920a996f3a96f058464f1d33e1f38"
        client_secret = "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"
        post_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': 'http://localhost:3000/callback'
            }
        response = requests.post("https://api.intra.42.fr/oauth/token/", data=post_data)

        access_token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        content = response.json()
        logging.warning('id: ' + str(content["id"]))    #debug
        logging.warning('username: ' + content["login"])    #debug
        logging.warning('email: ' + content["email"])    #debug
        return Response('', status.HTTP_200_OK)