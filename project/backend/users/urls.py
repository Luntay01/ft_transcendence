from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='users-home'),  # You can modify the view later
]