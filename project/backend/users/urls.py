#from django.urls import path
#from . import views

#urlpatterns = [
#    path('', views.index, name='users-home'),  # You can modify the view later
#]

from django.urls import path
from .views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]