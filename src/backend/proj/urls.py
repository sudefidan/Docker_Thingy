from django.contrib import admin
from django.urls import path, re_path, include
from app import views
from app.views import login_user, logout_user, user_profile_view
from rest_framework import routers, serializers, viewsets
from app.views import get_users
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/token/verify/', TokenVerifyView.as_view()),
    path('api/register/', views.create_user.as_view()),
    path('api/login/', login_user.as_view()),
    path('api/logout/', logout_user.as_view()),
    path('api/protected/', views.protected_view.as_view()),
    path('api/user-profile/', user_profile_view.as_view(), name='user_profile'),
    #path('api/upload-profile-picture/', views.protected_view.as_view()),
    #path('api/get-profile-picture/', views.protected_view.as_view()),
    path('api/users/', get_users, name='get_users'),
    path('api/create_community/', views.create_community.as_view()),
    path('events/', EventListCreateView.as_view(), name='event-list-create')
]