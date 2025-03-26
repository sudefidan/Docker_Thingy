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
from .models import Community, CommunityMember, CommunityLeader, Subscribed, SocialType
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
            
            return Response({
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "profile_picture": profile_picture,
                "about": user.about if hasattr(user, 'about') else '',
                "social_type": social_type,
                "social_username": social_username,
                "interests": user.interests if hasattr(user, 'interests') else []
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
            if not username.isalnum() or len(username) < 3 or len(username) > 30:
                return Response({
                    "error": "Username must be 3-30 characters long and contain only letters and numbers"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # validate name fields
            first_name = data['first_name']
            last_name = data['last_name']
            if not first_name.isalpha() or not last_name.isalpha():
                return Response({
                    "error": "First and last names must contain only letters"
                }, status=status.HTTP_400_BAD_REQUEST)
            if len(first_name) < 2 or len(last_name) < 2:
                return Response({
                    "error": "First and last names must be at least 2 characters long"
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
            
            # validate social type
            valid_types = ['instagram', 'linkedin', 'twitter']
            if social_type.lower() not in valid_types:
                return Response({
                    "error": f"Invalid social type. Must be one of: {', '.join(valid_types)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # get or create the social type
            social_type_obj, _ = SocialType.objects.get_or_create(social_type=social_type.lower())
            
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
    
    def put(self, request):
        try:
            user = request.user
            interests = request.data.get('interests', [])
            
            # validate interests is a list
            if not isinstance(interests, list):
                return Response({
                    "error": "Interests must be a list"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # update user's interests
            user.interests = interests
            user.save()
            
            return Response({
                "message": "Interests updated successfully",
                "interests": user.interests
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": "Failed to update interests",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
