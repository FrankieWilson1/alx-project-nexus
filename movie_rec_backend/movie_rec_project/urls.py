"""
URL configuration for movie_rec_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from movies.views import user_registration_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Movie endpoint
    path('api/', include('movies.urls')),

    # endpoints for obtaining token
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    # User registration endpoint
    path(
        'api/register/',
        user_registration_view,
        name='user_registration'
    ),
]
