from django.urls import path
from . import views
from .views import ExampleView

urlpatterns = [
    path('ping/', views.ping, name='ping'),  # Ensure this is present
    path('example/', ExampleView.as_view())
]