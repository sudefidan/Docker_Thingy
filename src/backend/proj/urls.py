from django.contrib import admin
from django.urls import path, re_path, include
from app import views
from .views import login_user
from rest_framework import routers, serializers, viewsets
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
    path('login/', login_user.as_view()),
    path('api/protected/', views.protected_view.as_view()),
]