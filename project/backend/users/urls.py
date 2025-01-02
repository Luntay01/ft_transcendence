from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import UserRegisterView, OauthCodeView, TokenObtainPairView

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    path('oauth/', OauthCodeView.as_view()),
]