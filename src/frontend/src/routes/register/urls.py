from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    path("api/register", views.create_register, name="create_register"),
]