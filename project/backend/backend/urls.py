"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin
#from django.urls import path, include
#from django.http import HttpResponse
#
#def home(request):
#    return HttpResponse("Welcome to the homepage!")
#
#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('', home),
#    path('pong/', include('pong.urls')),    # Include pong app URLs
#    path('users/', include('users.urls')),  # Include users app URLs
#    path('game/', include('game.urls')),    # Include game app URLs
#    path('chat/', include('chat.urls')),    # Include chat app URLs
#    path('api/', include('api.urls')),      # Include API app URLs
#]

from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # Adjust the path as needed
    path('api/', include('api.urls')),
    re_path(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework"))
]
