from django.core.cache import cache
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
    action
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
)

from .models import (
    Movie,
    FavoriteMovie,
    Comment,
    Like,
    Recommendation,
    PersonalizedRecommendation
)
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    UserRegistrationSerializer,
    MovieSerializer,
    FavoriteMovieSerializer,
    CommentSerializer,
    LikeSerializer,
    UserSerializer,
    RecommendationSerializer,
    PersonalizedRecommendationSerializer
)
from .tasks import fetch_and_save_recommendations as rec_task
from movie_rec_project.pagination import StandardResultsSetPagination


class BaseUserObjectViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet,
    RetrieveModelMixin,
    UpdateModelMixin
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
        # Ensures the user is set correctly during creation
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Returns a list of objects for the currently authenticated user.
        """
        # Filters the base queryset by the authenticated user.
        return self.queryset.filter(user=self.request.user)


class MovieViewSet (viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing movies. This is read-only.
    Optimized to annotate likes/comments and prefetch related data.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = [
        'id',
        'title',
        'release_date',
        'rating',
    ]

    # Search filtering (by id, title, overview, or cast name)
    search_fields = [
        'third_party_id',
        'title',
        'overview',
        'cast__name'
    ]

    def get_queryset(self):
        """
        Annotates total likes/comments and pre-fetches related data
        efficiently.
        """
        return Movie.objects.all().annotate(
            total_likes=Count(
                'like',
                distinct=True
            ),
            total_comments=Count(
                'comment',
                distinct=True
            )
        ).prefetch_related(
            'genres',
            'cast'
        )

    # Action to manually trigger a recommendation calculation for a movie
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def trigger_recommendation(self, request, pk=None):
        """
        Triggers a Celery task to fetch/recalculate recommendations for
        this movie.
        """
        rec_task.delay(pk)  # PK is the movie_id

        return Response(
            {
                "message": (
                    f"Recommendation calculation triggered for Movie ID '{pk}' "
                    f"in the background."
                )
            },
            status=status.HTTP_202_ACCEPTED
        )


class FavoriteMovieViewSet(BaseUserObjectViewSet):
    """
    A viewset for a user's favorite movies.
    Inherits from BaseUserObjectViewSet
    """
    queryset = FavoriteMovie.objects.all().select_related('movie')
    serializer_class = FavoriteMovieSerializer

    def create(self, request, *args, **kwargs):
        movie_id = request.data.get('movie')

        if not movie_id:
            return Response(
                {"error": "The 'movie' ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            favorite_instance, created = (
                FavoriteMovie.objects.update_or_create(
                    user=request.user,
                    movie_id=movie_id,
                    defaults={}
                )
            )

            serializer = self.get_serializer( favorite_instance)

            if created:
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK  # Already favorited
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CommentViewSet(BaseUserObjectViewSet):
    """
    A viewset for managing an authenticated user's own comments.
    """
    queryset = Comment.objects.all().select_related('user', 'movie')
    serializer_class = CommentSerializer

    # def perform_create(self, serializer):
    #     """
    #     Sets the user field automatically to the request.user.
    #     """
    #     serializer.save(user=self.request.user)

    # def get_queryset(self):
    #     """
    #     Filters Comments by movie ID if requested via query parameter.
    #     """
    #     queryset = self.queryset
    #     movie_id = self.request.query_params.get('movie')
    #     if movie_id is not None:
    #         queryset = queryset.filter(movie_id=movie_id)
    #         return queryset
        
    #     return queryset.filter(user=self.request.user)
    pass


class MovieCommentListAPIView(ListAPIView):
    """
    Allows any user (public) to view all comments for a specific movie.
    """
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']

        return Comment.objects.filter(
            movie_id=movie_id
        ).select_related(
            'user',
        ).order_by('-created_at')


class LikeViewSet(BaseUserObjectViewSet):
    """
    A viewset for user likes on movies, implementing idempotent creation and
    deletion.
    """
    queryset = Like.objects.all().select_related('movie')
    serializer_class = LikeSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Handles Post request: Creates a Like object, or returns 200 OK if it
        already exists
        """
        movie_id = request.data.get('movie')

        if not movie_id:
            return Response(
                {"error": "The 'movie' ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            like_instance, created = (
                Like.objects.update_or_create(
                    user=request.user,
                    movie_id=movie_id,
                    defaults={}
                )
            )

            serializer = self.get_serializer(like_instance)

            if created:
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(3)},
                status=status.HTTP_400_BAD_REQUEST
            )


# DRF decorator that turns a standard Django func. into an API view
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


class UserProfileView(RetrieveAPIView):
    """
    View to retrieve the user's profile.
    This view allows authenticated users to access their profile information

    Attributes:
        serializer_class: The serializer class used to serialize the user data.
        permission_classes: The permission classes that determine access to
        the view.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """ Return the current authenticated user """
        return self.request.user


class RecommendationListAPIView(ListAPIView):
    """
    Lists all recommendations for a specific movie (Item-to-Item)
    with pagination.

    Attributes:
        serializer_class: The serializer class used to serialize the
            recommedation data.
        permission_classes: The permission classes that allow read-only access
            to anyone.
        pagination_class: the class used for paginating the results.
    """
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']

        return Recommendation.objects.filter(
            source_movie_id=movie_id
        ).select_related('recommended_movie').order_by('-score')


class RecommendationForUserAPIView(ListAPIView):
    """
    Lists personalized movie recommedations for the authenticated user.

    Attributes:
        serializer_class: The serializer class used to serialize the
            personalized recommendation data.
        permission_classes: The permission classes that determine access to
        the view.
        pagination_class: the class used for paginating the results.
    """
    serializer_class = PersonalizedRecommendationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return PersonalizedRecommendation.objects.filter(
            user=self.request.user
        ).select_related('recommended_movie').order_by('-score')
