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
from .models import Community, CommunityLeader, Subscribed, Notification
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

    def post(self, request):
        try:
            data = request.POST
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            # if these fields are not filled in then error, make sure to put in details :D
            if not all([username, password, first_name, last_name, email]):
                return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
            user.access_level = data.get('access_level', 1)
            user.save()
            # refresh access token instead of regular so user no longer has to log in and it be annoying it will just refresh :D
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            # check response that shit is working :D
            return Response({
                'message': 'User created successfully',
                'access': access_token,
                'refresh': refresh_token
            }, status=status.HTTP_201_CREATED)

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
    # post request to send off the following variables
    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description')
        category = request.data.get('category')
        leader_ids = request.data.get('leader_ids', [])
        # check if users is authenticated
        if request.user.is_authenticated:
            owner_id = request.user.id
        else:
            return Response({"error": "User must be logged in"}, status=400)
          
        if Community.objects.filter(name__iexact=name).exists():
            return Response({"error": "This community already exists."}, status=400)

        # create the record in the database with these variables
        community = Community.objects.create(
            name=name,
            description=description,
            category=category,
            owner_id=owner_id
        )
        # create the link between the leader and the community
        for leader_id in leader_ids:
            user = get_object_or_404(User, id=leader_id)
            CommunityLeader.objects.create(community=community, user=user)
            Subscribed.objects.create(community=community, user=user)
            
        # auto subscribe the current userid that is logged to the community
        Subscribed.objects.create(community=community, user_id=owner_id)

        return Response({
            "community_id": community.community_id,
            "message": "Community created successfully and selected leaders assigned"
        })
    
class SubscribedCommunities(APIView):
    # the user must be logged in otherwise it will not work
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user
        # Fetch all subscriptions where user_id matches the currently logged in user.
        subscriptions = Subscribed.objects.filter(user=user)
        # Get the list of communities that have been subscribed too
        communities = [sub.community for sub in subscriptions]
        
        # Serialize the response
        community_data = [
            {
                "id": community.community_id,
                "name": community.name,
                "description": community.description,
                "category": community.category,
                "owner_id": community.owner_id
            } 
            for community in communities
        ]

        return Response({"subscribed_communities": community_data})

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
    communities = Community.objects.filter(community_id__in=
        Subscribed.objects.filter(user_id=user.id).values_list("community_id", flat=True)
    )

    community_data = [
        {
            'community_id': community.community_id,
            'name': community.name,
            'description': community.description,
            'category': community.category,
            'is_owner': community.owner_id == user.id
        }
        for community in communities
    ]
    
    return Response(community_data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_owned_communities(request):
    """Fetch all communities a user owns."""
    user = request.user
    communities = Community.objects.filter(owner=user)

    community_data = [
        {
            'community_id': community.community_id,
            'name': community.name,
            'description': community.description,
            'category': community.category,
            'is_owner': True  # Since these are owned communities
        }
        for community in communities
    ]

    return Response(community_data, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def leave_community(request):
        user = request.user
        community_id = request.data.get("community_id")

        try:
            membership = Subscribed.objects.get(user=user, community_id=community_id)
            membership.delete()
            return Response({"error": "Successfully left the community"})
        
        finally:
            return Response({"error": "You are not a member of this community"}, status=400)
        
        # except Subscribed.DoesNotExsist:
        #     return Response({"error": "You are not a member of this community"}, status=400)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_community_name(request):
    """
    Updates the name of a community based on the provided community_id.
    """
    try:
        community_id = request.data.get("community_id")
        community = get_object_or_404(Community, community_id=community_id)
    except ValueError:
        return Response({"error": "Invalid community ID."}, status=status.HTTP_400_BAD_REQUEST)

     # Check if the user is the owner
    if community.owner_id != request.user.id:
        return Response({"error": "You are not the owner of this community."}, status=status.HTTP_403_FORBIDDEN)

    new_name = request.data.get("value")

    if not new_name:
        return Response({"error": "New community name is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a community with the new name already exists
    if Community.objects.filter(name__iexact=new_name).exclude(community_id=community_id).exists():
        return Response({"error": "A community with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Get all users subscribed to the community
    subscribed_users = Subscribed.objects.filter(community=community)

    # Create notifications for each subscribed user
    for subscription in subscribed_users:
        user = subscription.user
        message = f"The community '{community.name}' has changed it's name to '{new_name}'."
        create_notification(user.id, message)

    community.name = new_name
    community.save()

    return Response({"message": "Community name updated successfully."}, status=status.HTTP_200_OK)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_community_description(request):
    """Updates the description of a community."""
    try:
        community_id = request.data.get("community_id")
        community = get_object_or_404(Community, community_id=community_id)
    except ValueError:
        return Response({"error": "Invalid community ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is the owner
    if community.owner_id != request.user.id:
        return Response({"error": "You are not the owner of this community."}, status=status.HTTP_403_FORBIDDEN)

    new_description = request.data.get("value")

    if new_description is None:
        return Response({"error": "New community description is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Get all users subscribed to the community
    subscribed_users = Subscribed.objects.filter(community=community)

    # Create notifications for each subscribed user
    for subscription in subscribed_users:
        user = subscription.user
        message = f"The community '{community.name}' has changed it's description to '{new_description}'."
        create_notification(user.id, message)

    community.description = new_description
    community.save()

    return Response({"message": "Community description updated successfully."}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_community_category(request):
    """Updates the category of a community."""
    try:
        community_id = request.data.get("community_id")
        community = get_object_or_404(Community, community_id=community_id)
    except ValueError:
        return Response({"error": "Invalid community ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is the owner
    if community.owner_id != request.user.id:
        return Response({"error": "You are not the owner of this community."}, status=status.HTTP_403_FORBIDDEN)

    new_category = request.data.get("value")

    if new_category is None:
        return Response({"error": "New community category is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Get all users subscribed to the community
    subscribed_users = Subscribed.objects.filter(community=community)

    # Create notifications for each subscribed user
    for subscription in subscribed_users:
        user = subscription.user
        message = f"The community {community.name} has changed it's category to '{new_category}' from '{community.category}'."
        create_notification(user.id, message)

    community.category = new_category
    community.save()

    return Response({"message": "Community category updated successfully."}, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_community(request, community_id):
    """Deletes a community if the user is the owner."""
    try:
        community = get_object_or_404(Community, community_id=community_id)
    except ValueError:
        return Response({"error": "Invalid community ID format."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is the owner
    if community.owner_id != request.user.id:
        return Response({"error": "You are not the owner of this community."}, status=status.HTTP_403_FORBIDDEN)

    message = "Community deleted successfully."

    # Get all users subscribed to the community
    subscribed_users = Subscribed.objects.filter(community=community)

    # Create notifications for each subscribed user
    for subscription in subscribed_users:
        user = subscription.user
        message = f"The community '{community.name}' has been deleted."
        create_notification(user.id, message)

    community.delete()
    return Response({"message": message}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    try:
        try:
            user = request.user.id
        except:
            return Response({"message": "Could not get user."}, status=status.HTTP_400_BAD_REQUEST)
        notifications = Notification.objects.filter(user=user)

        notification_data = [
            {
                'notification_id': notification.notification_id,
                'user': notification.user.id,
                'message': notification.message,
                'timestamp': notification.timestamp,
            }
            for notification in notifications
        ]

        return Response(notification_data, status=200)
    except:
        return Response({"message": "Could not get notifications."}, status=status.HTTP_400_BAD_REQUEST)


def create_notification(user_id, message):
    """
    Creates a notification for a given user.
    """
    try:
        # Retrieve the user object using get_object_or_404 to handle non-existent users
        user = get_object_or_404(User, id=user_id)

        # Create the notification object
        Notification.objects.create(user=user, message=message)
        return True
    except Exception as e:
        print(f"Error creating notification: {e}")
        return False

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Deletes a notification"""
    try:
        notification = get_object_or_404(Notification, notification_id=notification_id)
    except ValueError:
        return Response({"error": "Invalid notification ID format."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is the owner
    if notification.user.id != request.user.id:
        return Response({"error": "You are not the recipient of this notification."}, status=status.HTTP_403_FORBIDDEN)

    notification.delete()
    message = "Notification deleted successfully."
    return Response({"message": message}, status=status.HTTP_200_OK)