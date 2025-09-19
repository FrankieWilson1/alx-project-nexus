from django.db import models
from django.conf import settings


class Movie(models.Model):
    """
    Model to store movie data fetched from the third-party API.

    Attributes:
        title (str): The main title or name of the movie
        third_party_id (int): An ID of the third party api.
        poster_url (url): The url of an image of the movie.
        release_date (DateTime): Timestamp of the movie
    """
    title = models.CharField(max_length=255)
    third_party_id = models.IntegerField(unique=True)
    poster_url = models.URLField(max_length=500, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        """
        Returns the string representation of the title object
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
        unique_together = ('user', 'movie', )

    def __str__(self):
        return f"{self.user.username} favorited {self.movie.title}"
