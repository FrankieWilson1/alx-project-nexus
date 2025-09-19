from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from .models import Movie, FavoriteMovie, Comment, Like


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    A serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type:': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type:': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password2'
        )
        extra_kwargs = {
            'write_only': True
        }

    def validate(self, attrs):
        # Validates user password
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        # Create user after user has been validated.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(
            validated_data['password']
        )
        user.save()
        return user


class MovieSerializer(serializers.ModelSerializer):
    """
    A movie serilizer, converts django models to JSON data
    """
    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ('third_party_id', )


class FavoriteMovieSerializer(serializers.ModelSerializer):
    """
    FavoriteMovie serilizer class
    """
    class Meta:
        model = FavoriteMovie
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment Serializer class
    Attributes:
        user (Serializer): converts User model to JSON data
        movie (Serializer): converts Movie model to JSON data
    """
    user = serializers.ReadOnlyField(source='user.username')
    movie = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'movie',
            'text',
            'created_at'
        ]
        read_only_fields = (
            'user',
            'movie',
            'created_at'
        )


class LikeSerializer(serializers.ModelSerializer):
    """
    Like Serilizer class
    Attributes:
        user (Serializer): converts User model to JSON data
        movie (Serializer): converts Movie model to JSON data
    """
    user = serializers.ReadOnlyField(source='user.username')
    movie = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Like
        fields = [
            'id',
            'user',
            'movie',
            'created_at'
        ]
        read_only_fields = (
            'user',
            'movie',
            'created_at'
        )
