from django.contrib import admin
from django.urls import path, re_path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', views.index),
    path('api/example/', views.example_view),
    path('api/register', views.create_register),
    # path('', include('register.urls')),
    re_path(r'^(?P<path>.*)$', views.svelte_view),
]