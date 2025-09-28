from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    MovieViewSet,
    FavoriteMovieViewSet,
    CommentViewSet,
    LikeViewSet,
    user_registration_view,
    recommend_movies,
    RecommendationListAPIView,
    UserProfileView
)

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'favorites', FavoriteMovieViewSet, basename='favorite')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')

urlpatterns = [
    path(
        'register/',
        user_registration_view,
        name='register'
    ),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path(
        'movies/<int:movie_id>/recommendations/trigger/',
        recommend_movies,
        name='recommended-movies-trigger'
    ),
    path(
        'movies/<int:movie_id>/recommendations/',
        RecommendationListAPIView.as_view(),
        name='movie-recommendations-list'
    ),
] + router.urls
