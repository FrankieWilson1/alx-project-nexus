from rest_framework import serializers
from django.contrib.auth import get_user_model

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
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class MovieSerializer(serializers.ModelSerializer):
    """
    A movie serilizer, converts django models to JSON data
    """
    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ('third_party_id', )

    def get_total_likes(self, obj):
        return obj.like_set.count()
    
    def get_total_comments(self, obj):
        return obj.comment_set.count()


class FavoriteMovieSerializer(serializers.ModelSerializer):
    """
    FavoriteMovie serilizer class
    """
    class Meta:
        model = FavoriteMovie
        fields = [
            'id',
            'user',
            'movie',
            'created_at'
        ]
        read_only_fields = ['user', 'created_at']

    def validate(self, attrs):
        user = self.context['reqeust'].user
        movie = attrs.get('movie')
        if FavoriteMovie.objects.filter(user=user, movie=movie).exits():
            raise serializers.ValidationError({
                "detail": "You have already favorited this movie."
            })
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment Serializer class
    """
    user = serializers.ReadOnlyField(source='user.username')
    # movie = serializers.ReadOnlyField(source='movie.title')

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
            # 'movie',
            'created_at'
        )


class LikeSerializer(serializers.ModelSerializer):
    """
    Like Serilizer class
    """
    user = serializers.ReadOnlyField(source='user.username')

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
            'created_at'
        )

    def validate(self, attrs):
        user = self.context['request'].user
        movie = attrs.get('movie')
        if Like.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError(
                "You have already liked this movie."
            )
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id', 'username', 'email',)
