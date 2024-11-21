from django.urls import path
from .views import UserRegisterView, UserLoginView

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('login/', UserLoginView.as_view(), name='detail'),
]