from django.http import Http404
from django.core.mail import EmailMessage
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from .models import User
from .gmail_service import get_gmail_service, send_email
from .otp import generate_otp, verify_otp

class UserView(views.APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def verify_email(self, address):
        service = get_gmail_service()
        subject = "Verify Email"
        user = User.objects.get(email=address, provider='Pong')
        message = f'This is one-time password.\nVerify it within 24 hours.\n\n{generate_otp(user)}'
        send_email(service, address, subject, message)
        return
    
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(instance=users, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    # TODO: update if user is not verified yet
    # TODO: fail if user is already verified
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data, partial=True)
        if not (serializer.is_valid()):
            return Response({'error', 'Data is invalid. Failed to create user'}, status.HTTP_422_UNPROCESSABLE_ENTITY)
        serializer.save()
        # send verification mail
        self.verify_email(serializer.data['email'])
        return Response(serializer.data, status.HTTP_201_CREATED)

    def patch(self, request):
        user: User = request.user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if not (serializer.is_valid()):
            return Response({'error': 'Data is invalid. Failded to update user'}, status.HTTP_422_UNPROCESSABLE_ENTITY)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

class EmailVerifyView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request, fromat=None):
        user = User.objects.get(email=request.data['email'], provider='Pong')
        if user.is_verified:
            return Response({'message': 'Email has been already verified'}, status.HTTP_200_OK)
        verify_code = request.data['verify_code']
        if verify_otp(user, verify_code):
            user.is_verified = True
            user.save()
            return Response({'message': 'Email verified'}, status.HTTP_200_OK)
        return Response({'error': 'Invalid OTP'}, status.HTTP_401_UNAUTHORIZED)

class MeView(views.APIView):
    def get(self, request, format=None):
        user: User = request.user
        serializer = UserSerializer(instance=user)
        return Response(serializer.data, status.HTTP_200_OK)

class UserDetailView(views.APIView):
    # TODO: handle error case
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except Http404:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, username, format=None):
        user = self.get_object(username)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data, status.HTTP_200_OK)