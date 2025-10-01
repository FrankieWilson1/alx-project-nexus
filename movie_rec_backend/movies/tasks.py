# from movie_rec_project.celery import app as celery_app
# from celery import shared_task
import requests
import logging
from django.conf import settings
from django.db import transaction

from .models import (
    Movie,
    Recommendation,
    Genre,
    CastMember
)

logger = logging.getLogger(__name__)

TMDB_IMG_BASE_URL = "https://image.tmdb.org/t/p/w500/"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"


# @shared_task
def fetch_and_save_movie_details(movie_pk: int, api_key: str):
    """
    Helper function to fetch detailed data (overview, runtime, genres, cast)
    and update the Movie object.
    """
    try:
        movie = Movie.objects.get(pk=movie_pk)
    except Movie.DoesNotExist:
        logger.warning(
            f"Movie with PK {movie_pk} not found. Skipping detail fetch."
        )
        return

    tmdb_id = movie.third_party_id

    # Fetch details (overview, runtime, genres)
    details_url = f"{TMDB_BASE_URL}{tmdb_id}"
    logger.info(f"Fetching details for movie ID: {tmdb_id}")

    try:
        details_response = requests.get(
            details_url,
            params={'api_key': api_key}
        )
        details_response.raise_for_status()
        details_data = details_response.json()

        movie.overview = details_data.get('overview')
        movie.duration_minutes = details_data.get('runtime')

        # Save movie to ensure it's up-to-date before updating M2M fields
        movie.save()

        movie.genres.clear()  # Clear existing genres to
        # prevent duplicates/stale data
        genre_names = [g.get('name') for g in details_data.get('genres', [])]

        for name in genre_names:
            genre, created = Genre.objects.get_or_create(name=name)
            movie.genres.add(genre)

    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching details for TMDb ID {tmdb_id}: {e}")

    credits_url = f"{TMDB_BASE_URL}{tmdb_id}/credits"
    logger.info(f"Fetching credits for movie ID: {tmdb_id}")

    try:
        credits_response = requests.get(
            credits_url,
            params={'api_key': api_key}
        )
        credits_response.raise_for_status()
        credits_data = credits_response.json()

        cast_list = credits_data.get('cast', [])[:5]

        movie.cast.clear()  # Clear existing cast to prevent
        # duplicates/stale data

        for member_data in cast_list:
            cast_name = member_data.get('name')
            if cast_name:
                cast_member, created = CastMember.objects.get_or_create(
                    name=cast_name
                )
                movie.cast.add(cast_member)

        logger.info(
            f"Updated genres and cast for movie: "
            "{movie.title}"
        )

    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching credits for TMDb ID {tmdb_id}: {e}")

    movie.save()


@shared_task
@transaction.atomic  # Ensures all DB operations
# (Movie/Recommendation/Genre/Cast) succeed or fail together
def fetch_and_save_recommendations(local_movie_pk):
    """
    Fetches and saves recommended movies for a given local movie PK,
    and populates details for all newly added movies.
    """
    api_key = settings.TMDB_API_KEY

    try:
        source_movie = Movie.objects.get(pk=local_movie_pk)

        # If the source movie is just a placeholder, fetch its details now.
        if not source_movie.overview or not source_movie.genres.exists():
            fetch_and_save_movie_details(source_movie, api_key)

        tmdb_movie_id = source_movie.third_party_id
        url = f"{TMDB_BASE_URL}{tmdb_movie_id}/recommendations"

        logger.info(
            f"Querying TMDb for recommendations using external ID: "
            "{tmdb_movie_id}"
        )
        response = requests.get(url, params={'api_key': api_key})
        response.raise_for_status()
        data = response.json()

        recommended_movies_data = data.get('results', [])

        if not recommended_movies_data:
            logger.info(
                f"No recommendations found for movie ID: "
                "{tmdb_movie_id}."
            )
            return

        for movie_data in recommended_movies_data:
            if not movie_data.get('title') or not movie_data.get('id'):
                continue

            third_party_id = movie_data.get('id')

            poster_path = movie_data.get('poster_path')
            poster_url = (
                f"{TMDB_IMG_BASE_URL}{poster_path}"
                if poster_path else None
            )
            release_date = movie_data.get('release_date') or None

            # Create/Update the recommended Movie entry
            recommended_movie, created = Movie.objects.update_or_create(
                third_party_id=third_party_id,
                defaults={
                    'title': movie_data.get('title'),
                    'poster_url': poster_url,
                    'release_date': release_date,
                    'overview': movie_data.get('overview'),
                }
            )

            if created or not recommended_movie.genres.exists():
                fetch_and_save_movie_details(recommended_movie, api_key)

            if created:
                logger.info(
                    f"Saved new recommended movie: "
                    "{recommended_movie.title}"
                )

            Recommendation.objects.update_or_create(
                source_movie=source_movie,
                recommended_movie=recommended_movie,
                defaults={}
            )
            logger.info(
                f"Created recommendation link: "
                "{source_movie.title} -> {recommended_movie.title}"
            )

    except Movie.DoesNotExist:
        logger.error(
            f"Source movie with local PK {local_movie_pk} "
            "does not exist locally."
        )
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching recommendations from TMDb: {e}")
