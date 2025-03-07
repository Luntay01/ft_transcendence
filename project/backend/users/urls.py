from django.urls import path
from .views import UserView, MeView, UserDetailView
from rest_framework import routers

urlpatterns = [
    path('', UserView.as_view()),
    path('me', MeView.as_view()),
    path('<str:username>', UserDetailView.as_view()),
]