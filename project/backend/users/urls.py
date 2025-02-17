from django.urls import path
from .views import UserView, MeView, UserDetailView

urlpatterns = [
    path('', UserView.as_view()),
    path('me', MeView.as_view()),
    path('<str:username>', UserDetailView.as_view()),
]