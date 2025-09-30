from django.db import models
from django.conf import settings
from django.db import models


class Genre(models.Model):
    """
    Represents a single movie genre (e.g., 'Action', 'Comedy').

    Attributes:
        name (str): The name of the genre. Must be unique.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CastMember(models.Model):
    """
    Represents a single cast member in a movie database.

    Attributes:
        name (str): The name of the cast member. Must be unique.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    """
    Model to store movie data fetched from the third-party API.

    Attributes:
        title (str): The main title or name of the movie.
        third_party_id (int): An ID of the third party API.
        poster_url (url): The URL of an image of the movie.
        release_date (DateTime): Timestamp of the movie.
        overview (str): A brief description or summary of the movie.
        duration_minutes (int): The length of the movie in minutes.
        genres (ManyToManyField): A relationship to the Genre model
                                representing the genres of the movie.
    """
    title = models.CharField(max_length=255)
    third_party_id = models.IntegerField(unique=True)
    poster_url = models.URLField(max_length=500, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    cast = models.ManyToManyField(
        CastMember,
        related_name='movies'
    )
    genres = models.ManyToManyField(
        'Genre',  # Assuming there's a Genre model
        related_name='movies',
        blank=True
    )

    def __str__(self):
        """
        Returns the string representation of the movie title.
        """
        return self.title


class FavoriteMovie(models.Model):
    """
    Model to track a user's favorite movies.

    Attributes:
        user (Foreignkey): The Foreignkey to a user model
        movie (Foreignkey): The Foreignkey to a movie model
        added_at (DateTimeField) Timestamp to record when the movie is added\
            to the user's favorite's lists
        """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie',)

    def __str__(self):
        return f"{self.user.username} favorited {self.movie.title}"


class Comment(models.Model):
    """
    Model for user comments on a movie.

    Attributes:
        user (Foreignkey): The Foreignkey to a user model
        movie (Foreignkey): The Foreignkey to a movie model
        text (Text): The content of the text
        created_at (DateTimeField): Timestamp to record when the\
            comment was added
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.movie.title}"


class Like(models.Model):
    """
    Model to track a user's 'like' on a movie.

    Attributes:
        user (Foreignkey): The Foreignkey to a user model
        movie (Foreignkey): The Foreignkey to a movie model
        created_at (DateTimeField): Timestamp to record when the\
            'like' was initiated
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Ensures a user can only 'like' a movie once
        """
        unique_together = ('user', 'movie',)

    def __str__(self):
        return f"{self.user.username} liked {self.movie.title}"


class Recommendation(models.Model):
    """
    Stores the list of recommended movies for a given movie.

    This table is populated by a Celery task.

    Attributes:
        source_movie (ForeignKey): The movie for which
                recommendations are made.
        recommended_movie (ForeignKey): The movie that is recommended.
        score (float): A score or rank from the recommendation algorithm.
        created_at (DateTime): Timestamp indicating when the
                recommendation was generated.
    """
    source_movie = models.ForeignKey(
        'Movie',
        on_delete=models.CASCADE,
        related_name='source_recommendations'
    )

    # The movie that is recommended
    recommended_movie = models.ForeignKey(
        'Movie',
        on_delete=models.CASCADE,
        related_name='target_recommendations'
    )

    # Optional: A score or rank from the recommendation algorithm
    score = models.FloatField(default=0.0)

    # Optional: Timestamp to know when it was generated
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures no duplicate recommendation pairs are saved
        unique_together = ('source_movie', 'recommended_movie')

    def __str__(self):
        return (
            f"Rec for {self.source_movie_movie.title} -> "
            f"{self.recommended_movie.title}"
        )
