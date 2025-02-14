from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests

def index(request):
    return JsonResponse({"message": "Welcome to the Django backend!"})

def example_view(request):
    data = {
        "key": "value",
        "another_key": "another_value"
    }
    return JsonResponse(data)

def svelte_view(request, path=''):
    svelte_url = f"http://svelte_frontend:4173/{path}"
    response = requests.get(svelte_url)
    return HttpResponse(response.content, status=response.status_code)