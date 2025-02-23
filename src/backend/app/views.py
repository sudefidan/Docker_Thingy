from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import requests
import json

def index(request):
    return JsonResponse({"message": "Welcome to the Django backend!"})

@csrf_exempt
def create_register(request):
    print('hit')
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(f"Data received: {data}")
            name = data.get("name", "")
            email = data.get("email", "")
            password = data.get("password", "")

            if not name or not email or not password:
                return JsonResponse({"error": "Name, email, and password are required"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

            user = User.objects.create_user(username=name, email=email, password=password)
            user.save()

            return JsonResponse({"message": "User registered successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)

def example_view(request):
    data = {
        "key": "value",
        "another_key": "another_value"
    }
    return JsonResponse(data)

def svelte_view(request, path=''):
    # Development URL
    svelte_url = f"http://svelte_frontend:5173/{path}"
    # Production URL
    # svelte_url = f"http://svelte_frontend:4173/{path}"
    response = requests.get(svelte_url)
    return HttpResponse(response.content, status=response.status_code)