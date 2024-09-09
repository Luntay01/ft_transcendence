from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='api-home'),  # You can modify the view later
]