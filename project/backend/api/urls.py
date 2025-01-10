from django.urls import path
from . import views
from .views import MeView, UserViewSet
from .views import OauthCodeView, TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('ping/', views.ping, name='ping'),  # Ensure this is present
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    path('oauth/', OauthCodeView.as_view()),
    path('me/', MeView.as_view()),
    path('profile/', UserViewSet.as_view({'get': 'list'})),
    path('profile/<str:username>/', UserViewSet.as_view({'get': 'retrieve'}))
]
