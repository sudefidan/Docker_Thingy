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
from .models import Community, CommunityMember, CommunityLeader, Subscribed
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt

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
            token.blacklist()

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
    

class create_community(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description')
        category = request.data.get('category')
        leader_ids = request.data.get('leader_ids', [])
        
        if request.user.is_authenticated:
            owner_id = request.user.id
        else:
            return Response({"error": "User must be logged in"}, status=400)

        if Community.objects.filter(name__iexact=name).exists():
            return Response({"error": "This community already exists."}, status=400)

        community = Community.objects.create(
            name=name,
            description=description,
            category=category,
            owner_id=owner_id
        )

        for leader_id in leader_ids:
            user = get_object_or_404(User, id=leader_id)
            CommunityLeader.objects.create(community=community, user=user)
            Subscribed.objects.create(community=community, user=user)

        return Response({
            "community_id": community.community_id,
            "message": "Community created successfully and selected leaders assigned"
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()
    users_data = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    return JsonResponse(users_data, safe=False, status=200)

class CreateCommunity(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description')
        category = request.data.get('category')
        leader_ids = request.data.get('leader_ids', [])

        if request.user.is_authenticated:
            owner_id = request.user.id
        else:
            return Response({"error": "User must be logged in"}, status=400)

        # Check if community with the same name already exists
        existing_community = Community.objects.filter(name=name).first()
        if existing_community:
            return Response({"error": "A community with this name already exists."}, status=400)

        # Create the new community
        community = Community.objects.create(
            name=name,
            description=description,
            category=category,
            owner_id=owner_id
        )

        Subscribed.objects.create(user=request.user, community=community)
        for leader_id in leader_ids:
            user = get_object_or_404(User, id=leader_id)
            CommunityLeader.objects.create(community=community, user=user)
            Subscribed.objects.create(community=community, user=user)

        return Response({
            "community_id": community.community_id,
            "message": "Community created successfully and selected leaders assigned"
        })

def fetch_communities(request):
    if request.method == "GET":
        communities = Community.objects.all().values()
        return JsonResponse(list(communities), safe=False)
    
    return JsonResponse({"error": "Invalid request"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_community(request, community_id):
    """Allow a user to join a community"""
    user = request.user
    community = get_object_or_404(Community, pk=community_id)

    # Check if the user is a member or leader
    if CommunityLeader.objects.filter(community=community, user=user).exists() or \
       Subscribed.objects.filter(community=community, user=user).exists():  # Assuming 'Subscribed' tracks memberships
        return Response({"message": "You are already a member or leader of this community!"}, status=200)

    # Proceed with the logic for adding the user to the community
    # For example, add to Subscribed, etc.
    Subscribed.objects.create(user=user, community=community)

    return Response({"message": "Successfully joined the community!"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_your_communities(request):
    """Fetch all communities a user has joined."""
    user = request.user
    communities = Community.objects.filter(subscribed__user=user) 

    community_data = [
        {
            'community_id': community.community_id,
            'name': community.name,
            'description': community.description,
            'is_owner': community.owner == user,
            'is_leader': CommunityLeader.objects.filter(community=community, user=user).exists()
        }
        for community in communities
    ]
    

    return Response(community_data)

    @api+view(["POST"])
    @permission_classes([IsAuthenticated])
    def leave_community(request):
        user = request.user
        community_id = request.data.get("community_id")

        try:
            membership = Subscribed.objects.get(user=user, community_id=community_id)
            membership.delete()
            return Response({"error": "Successfully left the community"})
        
        except Subscribed.DoesNotExsist:
            return Response({"error": "You are not a member of this community"}, status=400)
