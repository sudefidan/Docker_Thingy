from django.contrib import admin
from django.urls import path, re_path, include
from app import views
from app.views import login_user, logout_user, user_profile_view, upload_profile_picture, GetProfilePicture, change_password, update_user_profile, update_social_media, update_user_about, update_user_interests
from rest_framework import routers, serializers, viewsets
from app.views import get_users, join_community, fetch_communities, fetch_your_communities, leave_community, fetch_owned_communities, update_community_name, update_community_description, update_community_category, delete_community, get_notifications, delete_notification, get_community_leaders, delete_community_leader, add_community_leader
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # admin interface
    path('admin/', admin.site.urls),
    
    # authentication endpoints
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/token/verify/', TokenVerifyView.as_view()),
    
    # user management endpoints
    path('api/register/', views.create_user.as_view()),
    path('api/login/', login_user.as_view()),
    path('api/logout/', logout_user.as_view()),
    path('api/protected/', views.protected_view.as_view()),
    path('api/change-password/', change_password.as_view(), name='change_password'),
    
    # profile related endpoints
    path('api/user-profile/', user_profile_view.as_view(), name='user_profile'),
    path('api/update-profile/', update_user_profile.as_view(), name='update_profile'),
    path('api/upload-profile-picture/', upload_profile_picture.as_view(), name='upload_profile_picture'),
    path('api/get-profile-picture/', GetProfilePicture.as_view(), name='get_profile_picture'),
    path('api/update-social-media/', update_social_media.as_view(), name='update_social_media'),
    path('api/update-about/', update_user_about.as_view(), name='update_about'),
    path('api/update-interests/', update_user_interests.as_view(), name='update_interests'),
    
    # users endpoint
    path('api/users/', get_users, name='get_users'),

    # posts endpoint
    path('api/get_posts/', views.get_posts, name='get_posts'),
    path('api/create_posts/', views.create_post, name='create_post'),
    
    # community related endpoints
    path('api/create_community/', views.create_community.as_view()),
    path("api/communities/", fetch_communities, name="fetch_communities"),
    path("api/join_community/<int:community_id>/", join_community, name="join_community"),
    path('api/your_communities/', fetch_your_communities, name="fetch_your_communities"),
    path("api/leave_community/", leave_community, name="leave_community"),
    path('api/subscribed_communities/', views.SubscribedCommunities.as_view(), name='subscribed_communities'),
    path('api/fetch_owned_communities/', fetch_owned_communities, name="fetch_owned_communities"),
    path('api/communities/update_community_name/', update_community_name, name="update_community_name"),
    path('api/communities/update_community_description/', update_community_description, name="update_community_description"),
    path('api/communities/update_community_category/', update_community_category, name="update_community_category"),
    path('api/communities/delete/<int:community_id>/', delete_community, name="delete_community"),
    path('api/community/get_leaders/<int:community_id>/', get_community_leaders, name="get_community_leaders"),
    path('api/community/<int:community_id>/leaders/<int:leader_id>/delete/', delete_community_leader, name="delete_community_leaders"),
    path('api/community/<int:community_id>/leaders/<str:username>/add/', add_community_leader, name='add_community_leader'),
    # path('events/', EventListCreateView.as_view(), name='event-list-create')

    # notifications
    path('api/notifications/', get_notifications, name="get_notifications"),
    path('api/notifications/delete/<int:notification_id>/', delete_notification, name="delete_notification"),
]