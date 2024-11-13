from django.urls import path
from .views import UserRegisterView, UserRetrieveView

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('retrieve/<str:username>/', UserRetrieveView.as_view(), name='detail'),
]