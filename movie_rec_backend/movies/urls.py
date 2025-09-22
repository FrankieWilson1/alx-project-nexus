from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    MovieViewSet,
    FavoriteMovieViewSet,
    CommentViewSet,
    LikeViewSet,
    user_registration_view,
    recommend_movies,
    MovieRecommendationsView,
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
        'movies/<int:movie_id>/recommendations/',
        recommend_movies,
        name='recommend-movies'
    ),
    path(
        'recommendations/',
        MovieRecommendationsView.as_view(),
        name='movie-recommendations'
    ),
] + router.urls
