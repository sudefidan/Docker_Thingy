from django.contrib import admin
from django.urls import path, re_path, include
from app import views
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
    path('api/register/super/', views.create_super_user.as_view()),
    path('api/protected/', views.protected_view.as_view()),
    re_path(r'^(?P<path>.*)$', views.svelte_view),  # Serves Svelte app
]