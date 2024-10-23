#from django.shortcuts import render

# Create your views here.
#from django.http import HttpResponse

#def index(request):
#    return HttpResponse("Welcome to the users Home Page!")
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer