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
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema

from .models import Movie, FavoriteMovie, Comment, Like, Recommendation
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    UserRegistrationSerializer,
    MovieSerializer,
    FavoriteMovieSerializer,
    CommentSerializer,
    LikeSerializer,
    UserSerializer,
    RecommendationSerializer
)
from .tasks import fetch_and_save_recommendations as rec_task
from movie_rec_project.pagination import StandardResultsSetPagination


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
    pagination_class = StandardResultsSetPagination

    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)


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
@swagger_auto_schema(
    method='post',
    request_body=UserRegistrationSerializer
)
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
    rec_task.delay(movie_id)

    return Response(
        {
            "message": "Fetching recommendations in the background..."
        },
        status=status.HTTP_202_ACCEPTED
    )

        
class UserProfileView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class RecommendationListAPIView(ListAPIView):
    """
    Lists all recommendations for a specific movie, with pagination.
    """
    serializer_class = RecommendationSerializer 
    permission_classes = [IsAuthenticated]
    
    pagination_class = StandardResultsSetPagination 
    
    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        
        return Recommendation.objects.filter(
            source_movie_id=movie_id
        ).select_related('recommended_movie').order_by('-score') 
