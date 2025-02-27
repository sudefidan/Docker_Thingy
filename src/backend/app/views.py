from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    # Development URL
    svelte_url = f"http://svelte_frontend:5173/{path}"
    # Production URL
    # svelte_url = f"http://svelte_frontend:4173/{path}"
    response = requests.get(svelte_url)
    return HttpResponse(response.content, status=response.status_code)

class create_user(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            # Check for required fields
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            if not username or not password:
              return Response({'error':'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Use create_user for secure password hashing
            user = User.objects.create_user(username=username, password=password, email=email)
            user.access_level = data.get('access_level', 1)
            user.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({'error': f'Missing field: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class create_super_user(APIView):
    # Allowing any is definitely NOT a good idea, but class used for now as a test
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            # Check for required fields
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            if not username or not password:
              return Response({'error':'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Use create_user for secure password hashing
            user = User.objects.create_superuser(username=username, password=password, email=email)
            user.access_level = data.get('access_level', 3)
            user.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({'error': f'Missing field: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Testing JWT requirement
class protected_view(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'message': f'You are logged in as {user.username}!', 'access_level': user.access_level})