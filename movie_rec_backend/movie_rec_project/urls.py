"""
URL configuration for movie_rec_project project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



# Schema view configuration for Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Movie Recommendation API",
        default_version='v1',
        description=(
            "API docummentation for the Movie Recommendation backend project."
        ),
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="frankuwill101@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Authentication (Simple JWT)
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
    
    # Main Application Endpoints
    path('api/', include('movies.urls')),
    
    # DRF Default Login/Logout
    path('api-auth/', include('rest_framework.urls')),
    
    # API Documentation
    path('swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
