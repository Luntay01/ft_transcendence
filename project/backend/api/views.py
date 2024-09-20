from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse


def ping(request):
    return JsonResponse({"message": "pong"})