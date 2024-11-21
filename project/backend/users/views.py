from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserSerializer

class UserRegisterView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


# TODO: check password as well
# TODO: return proper response
class UserLoginView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        user = User.objects.filter(username=request.data['username'])
        if user:
            return Response("You login! Take a jwt!!")
        return Response("Incorrect match of username and password", status.HTTP_403_FORBIDDEN)