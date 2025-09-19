from rest_framework.routers import DefaultRouter

from .views import (
    MovieViewSet,
    FavoriteMovieViewSet,
    CommentViewSet,
    LikeViewSet
)

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'favorites', FavoriteMovieViewSet, basename='favorite')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')

urlpatterns = router.urls
