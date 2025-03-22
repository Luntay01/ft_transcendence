from django.http import Http404
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from .models import User

class UserView(views.APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(instance=users, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            user = User.objects.get(email=request.data['email'], provider=request.data['provider'])
            if user.is_verified:
                return Response({'error': 'User already exists'}, status.HTTP_409_CONFLICT)
            serializer = UserSerializer(instance=user, data=request.data, partial=True)
            if not (serializer.is_valid()):
                return Response({'error': 'Data is invalid. Failed to update user'}, status.HTTP_422_UNPROCESSABLE_ENTITY)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        except:
            serializer = UserSerializer(data=request.data, partial=True)
            if not (serializer.is_valid()):
                return Response({'error', 'Data is invalid. Failed to create user'}, status.HTTP_422_UNPROCESSABLE_ENTITY)
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

    def patch(self, request):
        user: User = request.user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if not (serializer.is_valid()):
            return Response({'error': 'Data is invalid. Failded to update user'}, status.HTTP_422_UNPROCESSABLE_ENTITY)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

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