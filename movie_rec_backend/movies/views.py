from rest_framework import viewsets, status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from rest_framework.viewsets import GenericViewSet

from .models import Movie, FavoriteMovie, Comment, Like
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    UserRegistrationSerializer,
    MovieSerializer,
    FavoriteMovieSerializer,
    CommentSerializer,
    LikeSerializer,
    UserSerializer
)
from .tasks import fetch_and_save_recommendations


class BaseUserObjectViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    """
    A base viewset for user-owned objects (favorites, comments, likes).
    Handles creation, listing, and deletion for the authenticated user.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Saves the authenticated user as the owner of the object.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Returns a list of objects for the currently authenticated user.
        """
        return self.queryset.filter(user=self.request.user)


class MovieViewSet (viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing movies. This is read-only.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        # Cache key for movie queryset
        cache_key = 'movie_queryset'
        
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = self.filter_queryset(self.get_queryset()) 
            cache.set(cache_key, list(queryset), 3600)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FavoriteMovieViewSet(BaseUserObjectViewSet):
    """
    A viewset for a user's favorite movies.
    Inherits from BaseUserObjectViewSet
    """
    queryset = FavoriteMovie.objects.all()
    serializer_class = FavoriteMovieSerializer


class CommentViewSet(BaseUserObjectViewSet):
    """
    A viewset for user comments on movies.
    Inherits from BaseUserObjectViewSet
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.all()
        movie_id = self.request.query_params.get('movie')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        return queryset


class LikeViewSet(BaseUserObjectViewSet):
    """
    A viewset for user likes on movies
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


# DRF decorator that turns a standard Django func. into an API view
# Accepts only POST requests.
@api_view(['POST'])
@permission_classes((AllowAny, ))
def user_registration_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_movies(request, movie_id):
    """
    Trigger a background task to fetch movie recommendations.
    """
    # Triggers Celery task
    fetch_and_save_recommendations(movie_id)

    return Response(
        {
            "message": "Fetching recommendations in the background..."
        },
        status=status.HTTP_202_ACCEPTED
    )


class MovieRecommendationsView(ListAPIView):
    """
    A view to list recommended movies for a specific movie
    """
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Movie.objects.order_by('-release_date')[:10]


class UserProfileView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
