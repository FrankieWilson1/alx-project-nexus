from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    MovieViewSet,
    FavoriteMovieViewSet,
    CommentViewSet,
    LikeViewSet,
    user_registration_view,
    RecommendationListAPIView,
    MovieCommentListAPIView,
    UserProfileView,
    RecommendationForUserAPIView
)

# Router for viewSets
router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'favorites', FavoriteMovieViewSet, basename='favorite')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')

# Standard URL patterns
urlpatterns = [
    # Auth/User Endpoints
    path(
        'register/',
        user_registration_view,
        name='register'
    ),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # Public Comment Listing
    path(
        'movies/<int:movie_id>/comments/',
        MovieCommentListAPIView.as_view(),
        name='movie-comments-list'
    ),

    # Item-to-Item Recommendation Endpoints
    path(
        'movies/<int:movie_id>/recommendations/',
        RecommendationListAPIView.as_view(),
        name='movie-recommendations-list'
    ),

    # Personalized Recommendation Endpoints (User-to-Item)
    path(
        'recommendations/me/',
        RecommendationForUserAPIView.as_view(),
        name='personalized-recommendations-list'
    ),
]

# Combine router URLs
urlpatterns += router.urls
