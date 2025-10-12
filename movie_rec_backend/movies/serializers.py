from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator

from .models import (
    Movie,
    FavoriteMovie,
    Comment,
    Like,
    Genre,
    CastMember,
    Recommendation,
    PersonalizedRecommendation
)


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    A serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password2'
        )

    def validate(self, attrs):
        # Validates user password
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        # Deletes 'password2' before creating
        validated_data.pop('password2')
        # Create user after user has been validated.
        user = User.objects.create_user(
            **validated_data
        )
        return user


class CastMemberSerializer(serializers.ModelSerializer):
    """Serializer for basic CastMember representation"""
    class Meta:
        model = CastMember
        fields = ('id', 'name')


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for basic Genre representation"""
    class Meta:
        model = Genre
        fields = ('id', 'name')


class SlimMovieSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for embedding movie details where only poster
    are needed
    """
    class Meta:
        model = Movie
        fields = ('id', 'title', 'poster_url')
        read_only_fields = fields


class MovieSerializer(serializers.ModelSerializer):
    """
    A serializer for the Movie model, designed to handle serilization
    of movie data, including related genres and cast members.

    Attributes:
        total_likes (ReadOnlyField): The total number of likes for the movie.
        total_comments (ReadOnlyField): The total number of comments for a
        a movie
        genres (GenreSerializer): A read-only list oof genres associated with
        the movie
        cast (CastMemberSerializer): A read-only list of cast members
        associated with the movie.
    """
    # Calculated Fields
    total_likes = serializers.ReadOnlyField()
    total_comments = serializers.ReadOnlyField()

    # Many-to-Many Fields
    genres = GenreSerializer(many=True, read_only=True)
    cast = CastMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = (
            'id',
            'title',
            'third_party_id',
            'poster_url',
            'release_date',
            'overview',
            'duration_minutes',
            'genres',
            'cast',
            'total_likes',
            'total_comments',
            'rating'
        )
        read_only_fields = ('third_party_id',)


class FavoriteMovieSerializer(serializers.ModelSerializer):
    """
    FavoriteMovie serilizer class
    Handles the representation of favorite movies, including user information
    and associated movie details.

    Attributes:
        user (PrimaryKeyRelatedField): The user who favorited the movie.
        user_name (ReadOnlyField): The username of the user who favorited
        the movie.
        movie_title (ReadOnlyField): The title of the favorited movie.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_name = serializers.ReadOnlyField(
        source='user.username'
    )
    movie_title = serializers.ReadOnlyField(
        source='movie.title'
    )

    class Meta:
        model = FavoriteMovie
        fields = [
            'id',
            'user',
            'movie',
            'user_name',
            'movie_title',
            'created_at'
        ]
        read_only_fields = ['user', 'user_name', 'movie_title', 'created_at']

    validators = [
        UniqueTogetherValidator(
            queryset=FavoriteMovie.objects.all(),
            fields=['user', 'movie'],
            message="You have already favorited this movie."
        )
    ]

    def validate_movie(self, movie):
        if not Movie.objects.filter(pk=movie.pk).exists():
            raise serializers.ValidationError("Movie not found")
        return movie


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for managing comments on movies.
    Handles serializer handles the representation of comments, including
    user information and associated movie details.

    Attributes:
        user (ReadOnlyField): The username of the user who made the comment.
        movie_title (ReadOnlyField): The title of the movie being commented on.
    """
    user = serializers.ReadOnlyField(source='user.username')
    movie_title = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'movie',
            'movie_title',
            'text',
            'created_at'
        ]
        read_only_fields = (
            'user',
            'movie_title',
            'created_at'
        )


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for managing likes on movies.
    Hangles representation of likes, including user information and the
    associated movie..
    """
    movie_details = SlimMovieSerializer(source='movie', read_only=True)
    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        write_only=True
    )
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = [
            'id',
            'user',
            'movie',
            'movie_details',
            'created_at'
        ]
        read_only_fields = (
            'id',
            'user',
            'created_at'
        )

        validators = [
            UniqueTogetherValidator(
                queryset=Like.objects.all(),
                fields=['user', 'movie'],
                message="You have already liked this movie."
            )
        ]

    def validate_movie(self, movie):
        if not Movie.objects.filter(pk=movie.pk).exists():
            raise serializers.ValidationError("Movie not found.")
        return movie


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id', 'username', 'email',)


class RecommendationSerializer(serializers.ModelSerializer):
    recommended_movie = MovieSerializer()

    class Meta:
        model = Recommendation
        fields = ['recommended_movie', 'id', 'score']


class PersonalizedRecommendationSerializer(serializers.ModelSerializer):
    recommended_movie = MovieSerializer()

    class Meta:
        model = PersonalizedRecommendation
        fields = ['recommended_movie', 'score']
