from django.urls import path
from . import views
from .views import OauthCodeView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    path('oauth/', OauthCodeView.as_view()),
    path('login/', LoginView.as_view()),
]
