from django.urls import path
from . import views
from .views import OauthCodeView, TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    path('oauth/', OauthCodeView.as_view()),
]
