from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models import User, UserSocial, Event
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.db.models import Q
import requests
import base64
import re
from .models import Community, CommunityLeader, Subscribed, SocialType, Post, Notification, EventType, User, PostImage, EventParticipant, UserInterest
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from .utils import create_notification, create_notification_community_interest
from django.views import View
from datetime import datetime


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
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        #this determines whether the user has inputted email or password.
        try:
            if '@' in identifier:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            else:
                username = identifier
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)    

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


# handles user profile data retrieval
# returns all user information including profile picture, social media, and personal details
# requires user to be authenticated
class user_profile_view(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            # get social media data
            social_media = UserSocial.objects.filter(user=user)
            social_type = [sm.social_type.social_type for sm in social_media]
            social_username = [sm.social_username for sm in social_media]

            # handle profile picture conversion
            profile_picture = ''
            if hasattr(user, 'profile_picture') and user.profile_picture:
                profile_picture = f"data:image/png;base64,{base64.b64encode(user.profile_picture).decode('utf-8')}"

            user_interests_qs = UserInterest.objects.filter(user=user)
            interests_list = [ui.interest for ui in user_interests_qs]
            return Response({
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "profile_picture": profile_picture,
                "about": user.about if hasattr(user, 'about') else '',
                "social_type": social_type,
                "social_username": social_username,
                "interests": interests_list,
            })

        except Exception as e:
            return Response({
                "error": "Failed to fetch user profile",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# handles profile picture uploads and storage
# accepts base64 encoded image data from frontend
# converts and stores as binary data in database

class upload_profile_picture(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # get current authenticated user
            user = request.user
            # get base64 image data from request
            base64_image = request.data.get('profile_picture')

            # validate that image data was provided
            if not base64_image:
                return Response({"error": "No image data provided"}, status=status.HTTP_400_BAD_REQUEST)

            # handle base64 data URL format
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]

            # convert base64 string to binary data for storage
            # this is necessary because we store images as binary in the database
            image_data = base64.b64decode(base64_image)

            # save the binary image data to user's profile
            # the profile_picture field is a BinaryField in the User model
            user.profile_picture = image_data
            user.save()

            # return success response with the base64 image
            # frontend needs this to display the image immediately
            return Response({
                "message": "Profile picture uploaded successfully",
                "profile_picture": f"data:image/png;base64,{base64_image}"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # handle any errors during upload process
            return Response({
                "error": "Failed to upload profile picture",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# retrieves user's profile picture in base64 format
# converts binary data from database back to base64 for frontend display
class GetProfilePicture(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # get current authenticated user
            user = request.user

            # check if user has a profile picture
            if user.profile_picture:
                # convert binary data back to base64 string
                # this is needed because frontend expects base64 format
                base64_image = base64.b64encode(user.profile_picture).decode("utf-8")

                # return the image in data URL format
                # this format is required for displaying in HTML img tags
                return Response({
                    "profile_picture": f"data:image/png;base64,{base64_image}"
                }, status=status.HTTP_200_OK)

            # if no profile picture exists, return null - placeholder icon is provided by frontend
            return Response({"profile_picture": None}, status=status.HTTP_200_OK)

        except Exception as e:
            # handle any errors during retrieval process
            return Response({
                "error": "Failed to fetch profile picture",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class create_community(APIView):
    permission_classes = [IsAuthenticated]
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

        create_notification_community_interest(community)

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

# get the current posts from the database
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts(request):
    posts = Post.objects.all().order_by('-date')
    
    posts_data = []
    for post in posts:
        community_id = post.community.community_id if post.community else None
        community_name = post.community.name if post.community else 'No Community'
        posts_data.append({
            'id': post.post_id,
            'title': post.title,
            'content': post.content,
            'date': post.date.isoformat(),
            'user_id': post.user.id,
            'username': post.user.username,
            'community_id': community_id,
            'community_name': community_name,
        })
    
    return JsonResponse(posts_data, safe=False, status=200)


# send the post from the backend to the database


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    if request.method == 'POST':
        print(request.data)  # Log incoming data to check what is sent from the frontend
        print(request.FILES) # Log uploaded files

        title = request.data.get('title')
        content = request.data.get('content')
        date = request.data.get('date')
        community_id = request.data.get('community_id')
        image_file = request.FILES.get('image')  # Get the uploaded image file

        if not title or not content:
            return Response({'error': 'Title and content are required!'}, status=400)

        # If no community_id is provided or it's empty set community to None
        if not community_id:
            community = None
        else:
            try:
                # Ensure the community exists
                community = Community.objects.get(community_id=community_id)
            except Community.DoesNotExist:
                return Response({'error': 'Community not found!'}, status=404)

        # Create a new post
        post = Post.objects.create(
            title=title,
            content=content,
            date=date,
            user=request.user,
            community=community  # If community is None, post will have no community
        )
        image_url = None
        # if an image is attached to the post this will handle it
        if image_file:
            try:
                image_data = image_file.read()
                post_image = PostImage.objects.create(
                    post=post,
                    image=image_data  
                )

            except Exception as e:
                print(f"Error saving image data: {e}")

        response_data = {
            'id': post.post_id,
            'title': post.title,
            'content': post.content,
            'user_id': post.user.id,
            'username': post.user.username,
            'community_id': post.community.community_id if post.community else None,
            'community_name': post.community.name if post.community else None,
        }


        return Response(response_data, status=201)

# Retrieves the post image from the database
@api_view(['GET'])
def get_post_image(request, post_id):
    try:
        post_image = PostImage.objects.get(post__post_id=post_id)
        if post_image.image:
            return HttpResponse(post_image.image, content_type='image/jpeg') 
        else:
            return HttpResponse(status=404)
    except PostImage.DoesNotExist:
        return HttpResponse(status=404)

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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def leave_community(request, community_id):
        user = request.user
        community = get_object_or_404(Community, pk=community_id)

        try:
            membership = Subscribed.objects.get(user=user, community=community)
            membership.delete()

            CommunityLeader.objects.filter(user=user, community=community).delete()

            return Response({"message": "Successfully left the community"})
        except Subscribed.DoesNotExist:
            return Response({"error": "You are not a member of this community"}, status=400)

        # except Subscribed.DoesNotExsist:
        #     return Response({"error": "You are not a member of this community"}, status=400)

# handles user password changes
# requires current password verification and new password
class change_password(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')

            # validate that both passwords are provided
            if not current_password or not new_password:
                return Response({
                    "error": "Both current and new passwords are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # verify current password is correct
            if not user.check_password(current_password):
                return Response({
                    "error": "Current password is incorrect"
                }, status=status.HTTP_400_BAD_REQUEST)

            # validate new password length
            if len(new_password) < 8:
                return Response({
                    "error": "New password must be at least 8 characters long"
                }, status=status.HTTP_400_BAD_REQUEST)

            # update password
            user.set_password(new_password)
            user.save()

            return Response({
                "message": "Password updated successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Failed to change password",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# handles user profile updates
# allows updating username, first name, last name, and email
class update_user_profile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = request.user
            data = request.data

            # validate required fields
            if not all([data.get('username'), data.get('first_name'), data.get('last_name'), data.get('email')]):
                return Response({
                    "error": "All fields are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # validate username format and length
            username = data['username']
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9\-_]*', username) or len(username) < 3 or len(username) > 30:
                return Response({
                    "error": "Username must be 3-30 characters long, start with a letter, and contain only letters, numbers, hyphens, or underscores"
                }, status=status.HTTP_400_BAD_REQUEST)

            # validate first name
            first_name = data['first_name']
            if not re.fullmatch(r'[A-Za-z]+', first_name):
                return Response({
                    "error": "First name must contain only letters"
                }, status=status.HTTP_400_BAD_REQUEST)

            if len(first_name) < 1:
                return Response({
                    "error": "First name must be at least 1 character long"
                }, status=status.HTTP_400_BAD_REQUEST)


            # validate last name
            last_name = data['last_name']
            if not re.fullmatch(r'[A-Za-z]+', last_name):
                return Response({
                    "error": "Last name must contain only letters"
                }, status=status.HTTP_400_BAD_REQUEST)

            if len(last_name) < 1:
                return Response({
                    "error": "Last name must be at least 1 character long"
                }, status=status.HTTP_400_BAD_REQUEST)

            # validate email format
            email = data['email']
            if not '@' in email or not '.' in email:
                return Response({
                    "error": "Please enter a valid email address"
                }, status=status.HTTP_400_BAD_REQUEST)

            # check if username is already taken by another user
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                return Response({
                    "error": "Username is already taken"
                }, status=status.HTTP_400_BAD_REQUEST)

            # check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return Response({
                    "error": "Email is already in use"
                }, status=status.HTTP_400_BAD_REQUEST)

            # update user information
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            return Response({
                "message": "Profile updated successfully",
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Failed to update profile",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class update_social_media(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            social_type = request.data.get('social_type')
            social_username = request.data.get('social_username')

            # validate required fields
            if not social_type or not social_username:
                return Response({
                    "error": "Both social type and username are required"
                }, status=status.HTTP_400_BAD_REQUEST)


            # get or create the social type
            social_type_obj, _ = SocialType.objects.get_or_create(social_type=social_type)

            # get or create user social media entry
            user_social, created = UserSocial.objects.get_or_create(
                user=user,
                social_type=social_type_obj,
                defaults={'social_username': social_username}
            )

            if not created:
                user_social.social_username = social_username
                user_social.save()

            return Response({
                "message": "Social media updated successfully",
                "social_type": user_social.social_type.social_type,
                "social_username": user_social.social_username
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Failed to update social media",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            user = request.user
            social_type = request.data.get('social_type')

            if not social_type:
                return Response({
                    "error": "Social type is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # get the social type object
            try:
                social_type_obj = SocialType.objects.get(social_type=social_type.lower())
                # delete the social media entry
                UserSocial.objects.filter(user=user, social_type=social_type_obj).delete()
            except SocialType.DoesNotExist:
                return Response({
                    "error": "Invalid social type"
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "Social media removed successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Failed to remove social media",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# handles user's about section updates
# allows users to add or modify their bio/about section
# requires user to be authenticated
class update_user_about(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = request.user
            about = request.data.get('about', '')

            # update user's about section
            user.about = about
            user.save()

            return Response({
                "message": "About section updated successfully",
                "about": user.about
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Failed to update about section",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# handles user's interests/hobbies updates
# allows users to add, remove, or modify their interests
# requires user to be authenticated
class update_user_interests(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        try:
            user = request.user
            interests_list = request.data.get('interests', [])

            if not isinstance(interests_list, list):
                return Response({
                    "error": "Interests must be a list of strings"
                }, status=status.HTTP_400_BAD_REQUEST)

            if not all(isinstance(item, str) for item in interests_list):
                 return Response({
                    "error": "Each interest must be a string"
                }, status=status.HTTP_400_BAD_REQUEST)

            UserInterest.objects.filter(user=user).delete()

            new_interests = []
            for interest_text in interests_list:
                if interest_text: # Avoid saving empty strings if necessary
                    interest_obj = UserInterest.objects.create(user=user, interest=interest_text)
                    new_interests.append(interest_obj.interest) # Store the saved interest text

            return Response({
                "message": "Interests updated successfully",
                # Return the list of interests that were actually saved
                "interests": new_interests
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging
            print(f"Error updating interests for user {user.id}: {e}")
            return Response({
                "error": "Failed to update interests",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    create_notification_community_interest(community)

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
    except Exception as e:
        print(e)
        return Response({"message": "Could not get notifications."}, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_community_leaders(request, community_id):
    """
    Retrieves all users who are leaders of a specific community.
    """
    try:
        community = get_object_or_404(Community, community_id=community_id)
    except ValueError:
        return Response({"error": "Invalid community ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve all CommunityLeader objects associated with the community
    community_leaders = CommunityLeader.objects.filter(community=community)

    # Extract the user objects from the CommunityLeader objects
    leaders = [leader.user for leader in community_leaders]

    # Serialize the leader data
    leader_data = [
        {
            "user_id": leader.id,
            "username": leader.username,
            "email": leader.email,
            "first_name": leader.first_name,
            "last_name": leader.last_name,
        }
        for leader in leaders
    ]

    return Response(leader_data, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_community_leader(request, community_id, leader_id):
    """Deletes a community leader from a community"""
    try:
        community = get_object_or_404(Community, community_id=community_id)
        leader_to_remove = get_object_or_404(User, id=leader_id)
    except ValueError:
        return Response({"error": "Invalid community or user ID format."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the requesting user is the owner of the community
    if community.owner_id != request.user.id:
        return Response({"error": "You are not the owner of this community."}, status=status.HTTP_403_FORBIDDEN)

    try:
        community_leader = CommunityLeader.objects.get(community=community, user=leader_to_remove)
        community_leader.delete()
        message_leader = f"You are no longer a leader of {community.name}."
        create_notification(leader_id, message_leader)
        message_owner = f"User {leader_to_remove.username} is no longer a leader of {community.name}."
        create_notification(request.user.id, message_owner)
        return Response({"message": f"User {leader_to_remove.username} is no longer a leader of {community.name}."}, status=status.HTTP_200_OK)
    except CommunityLeader.DoesNotExist:
        return Response({"error": f"User {leader_to_remove.username} is not a leader of {community.name}."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_community_leader(request, community_id, user_id):
    """
    Adds a user as a leader to a community.
    """
    try:
        community = get_object_or_404(Community, community_id=community_id)
        user_to_add = get_object_or_404(User, id=user_id)
    except ValueError:
        return Response({"error": "Invalid community or user ID format."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the requesting user is the owner of the community
    if community.owner_id != request.user.id:
        return Response({"error": "You are not the owner of this community."}, status=status.HTTP_403_FORBIDDEN)

    # Check if the user is already a leader
    if CommunityLeader.objects.filter(community=community, user=user_to_add).exists():
        return Response({"error": f"User {user_to_add.username} is already a leader of {community.name}."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        CommunityLeader.objects.create(community=community, user=user_to_add)
        # Check if the user is already subscribed
        if not Subscribed.objects.filter(community=community, user=user_to_add).exists():
            # Subscribe the user to the community only if they are not already subscribed
            Subscribed.objects.create(community=community, user=user_to_add)
        message_leader = f"You are now a leader of {community.name}."
        create_notification(user_to_add.id, message_leader)
        message_owner = f"User {user_to_add.username} is now a leader of {community.name}."
        create_notification(request.user.id, message_owner)
        return Response({"message": f"User {user_to_add.username} is now a leader of {community.name}."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    data = request.data
    user = request.user

    EventType.objects.get_or_create(name='virtual')
    EventType.objects.get_or_create(name='in-person')

    # Extract fields from request.data
    title = data.get('title')
    description = data.get('description', '')
    date_str = data.get('date')
    virtual_link = data.get('virtual_link')
    location = data.get('location')
    event_type_name = data.get('event_type') 
    community_id = data.get('community_id')

    # Validate required fields
    if not all([title, date_str, event_type_name, community_id]):
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate date format
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate community and permissions
    community = get_object_or_404(Community, pk=community_id)
    try:
        event_type = EventType.objects.get(name=event_type_name)
    except EventType.DoesNotExist:
        return Response({"error": f"EventType '{event_type_name}' not found."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is an owner or a leader of the community
    is_owner = community.owner == user
    is_leader = CommunityLeader.objects.filter(community=community, user=user).exists()

    if not (is_owner or is_leader):
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    # Create event
    event = Event.objects.create(
        title=title,
        description=description,
        date=date,
        virtual_link=virtual_link,
        location=location,
        event_type=event_type,
        community=community
    )

    event.save

    return Response({"message": "Event created!", "event_id": event.event_id}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_events(request):
    # Retrieve all events for the authenticated user
    events = Event.objects.all()
    user = request.user

    # Prepare the event data for response
    event_list = [
        {
            'event_id': event.event_id,
            'title': event.title,
            'description': event.description,
            'date': event.date,
            'virtual_link': event.virtual_link,
            'location': event.location,
            'event_type': event.event_type.name if event.event_type else None,
            'community': event.community.name if event.community else None,
            'participant_count': EventParticipant.objects.filter(event=event).count(),
            'is_participating': EventParticipant.objects.filter(event=event, user=user).exists()
        }
        for event in events
    ]

    return Response(event_list, status=200)

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def event_handler(request):
#     # Handle POST method (Create Event)
#     if request.method == 'POST':
#         # Extract data from the request body
#         data = request.data
#         user = request.user

#         print(" Incoming Event Data:", data)

#         # Extract fields
#         title = data.get('title')
#         description = data.get('description', '')
#         date = data.get('date')
#         virtual_link = data.get('virtual_link')
#         location = data.get('location')
#         event_type_name = data.get('event_type')
#         community_id = data.get('community_id')

#         # Validate community and permissions
#         community = get_object_or_404(Community, pk=community_id)

#         try:
#             event_type = EventType.objects.get(name=event_type_name)
#         except EventType.DoesNotExist:
#             return Response({"error": f"EventType '{event_type_name}' not found."}, status=400)

#         # Check if the user is an owner or a leader of the community
#         is_owner = community.owner == user
#         is_leader = CommunityLeader.objects.filter(community=community, user=user).exists()

#         if not (is_owner or is_leader):
#             return Response({"error": "Permission denied."}, status=403)

#         # Create event
#         event = Event.objects.create(
#             title=title,
#             description=description,
#             date=date,
#             virtual_link=virtual_link,
#             location=location,
#             event_type=event_type,
#             community=community
#         )

#         return Response({"message": "Event created!", "event_id": event.event_id}, status=201)

#     # Handle GET method (List Events)
#     elif request.method == 'GET':
#         # Retrieve all events for the authenticated user
#         events = Event.objects.all()

#         # Prepare the event data for response
#         event_list = [
#             {
#                 'event_id': event.event_id,
#                 'title': event.title,
#                 'description': event.description,
#                 'date': event.date,
#                 'virtual_link': event.virtual_link,
#                 'location': event.location,
#                 'event_type': event.event_type.name if event.event_type else None,
#                 'community': event.community.name if event.community else None
#             }
#             for event in events
#         ]

#         return Response(event_list, status=200)

# get user profile for any user, allows for users to see other users profile.
class GetUserProfile(APIView):
    permission_classes = []

    def get(self, request, user_id):
        try:
            # Fetch user by ID
            user = User.objects.get(id=user_id)

            # Fetch social links associated with the user
            social_links = UserSocial.objects.filter(user=user).values('social_type__social_type', 'social_username')

            # Prepare the profile picture as Base64 string
            profile_picture_base64 = None
            if user.profile_picture:
                # Convert binary profile picture to Base64
                profile_picture_base64 = base64.b64encode(user.profile_picture).decode('utf-8')

            # Retrieve user profile data
            user_profile_data = {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "about": user.about, 
                "profile_picture": profile_picture_base64, 
                "social_links": [
                    {"social_type": link['social_type__social_type'], "social_username": link['social_username']}
                    for link in social_links
                ],
            }

            # Return profile data
            return Response(user_profile_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
    
            return Response({"error": "An error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeletePostView(APIView):

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            if post.user.id != request.user.id:
                return Response({"detail": "Not authorized to delete this post."}, status=status.HTTP_403_FORBIDDEN)
            
            post.delete()
            return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_event(request, event_id):
    """Allow a user to join an event"""
    user = request.user
    event = get_object_or_404(Event, pk=event_id)

    # Check if user is already a participant
    if EventParticipant.objects.filter(event=event, user=user).exists():
        return Response({"message": "You are already participating in this event!"}, status=status.HTTP_200_OK)

    # Add user as participant
    EventParticipant.objects.create(event=event, user=user)

    # Create notification for event creator
    message = f"{user.username} has joined your event '{event.title}'"
    create_notification(event.community.owner.id, message)

    return Response({"message": "Successfully joined the event!"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_event(request, event_id):
    """Allow a user to leave an event"""
    user = request.user
    event = get_object_or_404(Event, pk=event_id)

    # Check if user is a participant
    try:
        participant = EventParticipant.objects.get(event=event, user=user)
        participant.delete()
        
        # Create notification for event creator
        message = f"{user.username} has left your event '{event.title}'"
        create_notification(event.community.owner.id, message)
        
        return Response({"message": "Successfully left the event!"}, status=status.HTTP_200_OK)
    except EventParticipant.DoesNotExist:
        return Response({"error": "You are not participating in this event!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_managed_events(request):
    """
    Retrieves events where the authenticated user is either the owner
    or a leader of the associated community. Handles potential duplicates
    if a user is both owner and leader.
    """
    user = request.user

    try:
        # Query events using Q objects for complex lookups
        # Condition 1: User is the owner of the event's community
        # Condition 2: User is listed as a leader for the event's community
        managed_events_qs = Event.objects.filter(
            Q(community__owner=user) | Q(community__communityleader__user=user)
        ).select_related('community', 'event_type').prefetch_related('eventparticipant_set')
        # Serialize the event data and handle deduplication
        event_list = []
        processed_event_ids = set() # Keep track of event IDs already added

        for event in managed_events_qs:
            # Skip if this event has already been added
            if event.event_id in processed_event_ids:
                continue

            event_list.append({
                'event_id': event.event_id,
                'title': event.title,
                'description': event.description,
                'date': event.date.isoformat() if event.date else None, # Use isoformat for consistency
                'virtual_link': event.virtual_link,
                'location': event.location,
                'event_type': event.event_type.name if event.event_type else None,
                'community_id': event.community.community_id if event.community else None,
                'community_name': event.community.name if event.community else None,
                # You might want participant count or other details here too
                'participant_count': event.eventparticipant_set.count(), # Efficient count due to prefetch_related
                'is_participating': event.eventparticipant_set.filter(user=user).exists() # Check if current user participates
            })
            # Mark this event ID as processed
            processed_event_ids.add(event.event_id)

        return Response(event_list, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching managed events for user {user.username}: {e}")
        print(traceback.format_exc()) # Print full traceback
        return Response(
            {"error": "An error occurred while fetching manageable events."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@transaction.atomic # Ensure the update is atomic
def update_event_field(request):
    """
    Updates a specific field of an event if the user has permission.
    Expects a PATCH request with JSON body: {"field": "field_name", "value": "new_value"}
    """
    user = request.user

    # Get Request Data
    try:
        data = request.data
        field_to_update = data.get('field')
        new_value = data.get('value')
        event_id = data.get('eventId')

        if not field_to_update:
            return Response({"error": "The 'field' to update must be specified."}, status=status.HTTP_400_BAD_REQUEST)
        # Allow new_value to be None or empty string for fields like description, virtual_link, location

    except Exception as e:
        return Response({"error": "Invalid request data.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Get the Event and Check Permissions
    try:
        event = get_object_or_404(Event.objects.select_related('community', 'event_type'), pk=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Invalid event ID format."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is owner or leader of the event's community
    community = event.community
    if not community:
        # Should not happen if events always belong to a community, but good to check
        return Response({"error": "Event is not associated with a community."}, status=status.HTTP_400_BAD_REQUEST)

    is_owner = community.owner == user
    is_leader = CommunityLeader.objects.filter(community=community, user=user).exists()

    if not (is_owner or is_leader):
        return Response({"error": "You do not have permission to edit this event."}, status=status.HTTP_403_FORBIDDEN)

    # Validate and Update Field
    allowed_fields = ['title', 'description', 'date', 'virtual_link', 'location', 'event_type']

    if field_to_update not in allowed_fields:
        return Response({"error": f"Updating the field '{field_to_update}' is not allowed."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        original_value = getattr(event, field_to_update)

        # Field-specific validation and processing
        if field_to_update == 'title':
            if not new_value:
                return Response({"error": "Title cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
            setattr(event, field_to_update, str(new_value))

        elif field_to_update == 'description':
            # Allow empty description
            setattr(event, field_to_update, str(new_value) if new_value is not None else None)

        elif field_to_update == 'date':
            if not new_value:
                return Response({"error": "Date cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # Expecting 'YYYY-MM-DD' format from the frontend input type="date"
                parsed_date = datetime.strptime(str(new_value), '%Y-%m-%d').date()
                setattr(event, field_to_update, parsed_date)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        elif field_to_update == 'virtual_link':
             # Allow empty/null link
            setattr(event, field_to_update, str(new_value) if new_value else None)
            # Optional: Add URL validation here if needed

        elif field_to_update == 'location':
             # Allow empty/null location
            setattr(event, field_to_update, str(new_value) if new_value else None)

        elif field_to_update == 'event_type':
            if not new_value:
                 return Response({"error": "Event type cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # Find the EventType object by name
                event_type_obj = EventType.objects.get(name=str(new_value))
                setattr(event, field_to_update, event_type_obj)
                original_value = original_value.name if original_value else None # For notification message
            except EventType.DoesNotExist:
                return Response({"error": f"Invalid event type: '{new_value}'. Must be 'virtual' or 'in-person'."}, status=status.HTTP_400_BAD_REQUEST)

        # Notify participants
        participants = EventParticipant.objects.filter(event=event).select_related('user')
        for participant in participants:
            if participant.user != user: # Don't notify the editor
            if field_to_update == 'title':
                message = f"The title of an event has been updated to '{new_value}'!" 
            else:
                message = f"The details for event '{event.title}' have been updated. The {field_to_update} was changed to '{new_value}'!"
            create_notification(participant.user.id, message)


        event.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        # Log the error for debugging
        print(f"Error updating event {event_id} field '{field_to_update}' for user {user.username}: {e}")
        return Response(
            {"error": "An error occurred while updating the event."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )