from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat-home'),  # You can modify the view later
]