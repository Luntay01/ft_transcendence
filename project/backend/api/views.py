from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, JsonResponse


def ping(request):
    return JsonResponse({"message": "pong"})

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User


class MeView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user: User = request.user
        content = {
            'user': str(user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
            'is_superuser': str(user.is_superuser),
            'date_joined': str(user.date_joined),
            'birth_day': str(user.birth_day),
            'first_name': str(user.first_name),
        }
        return Response(content)

from rest_framework.viewsets import ViewSet
from users.serializers import ProfileSerializer
class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    
    def list(self, request):
        serializer = ProfileSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, username=None):
        item = get_object_or_404(self.queryset, username=self.kwargs['username'])
        serializer = ProfileSerializer(item)
        return Response(serializer.data)
