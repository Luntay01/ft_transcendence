from django.urls import path
from .views import UserGamesView, GameView

urlpatterns = [
    path('<str:username>', UserGamesView.as_view()),
    path('<int:game_id>', GameView.as_view()),
]
