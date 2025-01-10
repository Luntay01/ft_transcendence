from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer

class UserRegisterView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data, partial=True)
        if not (serializer.is_valid()):
            return Response('', status.HTTP_422_UNPROCESSABLE_ENTITY)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
