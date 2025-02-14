from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    return JsonResponse({"message": "Welcome to the Django backend!"})

def example_view(request):
    data = {
        "key": "value",
        "another_key": "another_value"
    }
    return JsonResponse(data)