from rest_framework import viewsets, status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.generics import ListAPIView

from .models import Movie, FavoriteMovie, Comment, Like
from .serializers import (
    UserRegistrationSerializer,
    MovieSerializer,
    FavoriteMovieSerializer,
    CommentSerializer,
    LikeSerializer
)
from .tasks import fetch_and_save_recommendations


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing movies. This is read-only.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        # Cache key for movie list
        cache_key = 'movie_list'
        cache_data = cache.get(cache_key)

        if cache_data:
            return Response(cache_data)

        # Fetches data from database if not cached
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data

        # Cache the data for a specific perioud of time.
        cache.set(cache_key, response_data, 3600)

        return Response(response_data)


class FavoriteMovieViewSet(viewsets.ModelViewSet):
    """
    A viewset for a user's favorite movies.
    """
    serializer_class = FavoriteMovieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns favorite movies for the currently authenticated user.
        """
        return FavoriteMovie.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        """
        Saves the authenticated user as the owner of the favorite movie.
        """
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for user comments on movies.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    """
    A viewset for user likes on movies
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
