from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models import User, UserSocial
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import InMemoryUploadedFile
import requests
import base64

def index(request):
    return JsonResponse({"message": "Welcome to the Django backend!"})

def example_view(request):
    data = {
        "key": "value",
        "another_key": "another_value"
    }
    return JsonResponse(data)

# def svelte_view(request, path=''):
#     # Development URL
#     svelte_url = f"http://svelte_frontend:5173/{path}"
#     # Production URL
#     # svelte_url = f"http://svelte_frontend:4173/{path}"
#     response = requests.get(svelte_url)
#     return HttpResponse(response.content, status=response.status_code)

class create_user(APIView):
    permission_classes = [AllowAny]

    # Usually use request.data, but since page has been switched to standard form it is sending FormData, which reqires request.POST
    def post(self, request):
        try:
            data = request.POST
            # Check for required fields
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            if not username or not password:
              return Response({'error':'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            if not first_name or not last_name:
              return Response({'error':'First and last name are required'}, status=status.HTTP_400_BAD_REQUEST)
            if not email:
              return Response({'error':'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Use create_user for secure password hashing
            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
            user.access_level = data.get('access_level', 1)
            user.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({'error': f'Missing field: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class login_user(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user: 
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
# Testing JWT requirement
class protected_view(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'message': f'You are logged in as {user.username}!', 'access_level': user.access_level})

class logout_user(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get('refresh')
            if not refresh:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh)
            token.blacklist() # This is to prevent reuse of token

            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
    
    
class user_profile_view(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        
        user = get_object_or_404(User, pk=user_id)
        
        return Response({
            "username": user.username,
            "forename": user.first_name,
            "surname": user.last_name,
            "email": user.email
        })
        
    
    
'''class upload_profile_picture(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if "profile_picture" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES["profile_picture"]
        
        if isinstance(file, InMemoryUploadedFile):
            user.profile_picture = file.read()
            user.save()
            return Response({"error": "Profile picture uploaded successfully"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid file"}, status=status.HTTP_400_BAD_REQUEST)
    
class GetProfilePicture(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        # Fetches users profile picture and returns it as a b64 string
        
        user = request.user
        if user.profile_picture:
            base64_image = base64.b64encode(user.profile_picture).decode("utf-8")
            return Response({"profile_picture": f"data:image/png;base64,{base64_image}"}, status=status.HTTP_200_OK)

        return Response({"profile_picture": None}, status=status.HTTP_200_OK)
'''