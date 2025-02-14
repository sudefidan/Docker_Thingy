from django.contrib import admin
from django.urls import path, re_path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', views.index),
    path('api/example/', views.example_view),
    re_path(r'^(?P<path>.*)$', views.svelte_view),
]