from django.urls import path
from . import views
from .views import MeView, UserViewSet

urlpatterns = [
    path('ping/', views.ping, name='ping'),  # Ensure this is present
    path('me/', MeView.as_view()),
    path('profile/', UserViewSet.as_view({'get': 'list'})),
    path('profile/<str:username>/', UserViewSet.as_view({'get': 'retrieve'}))
]
