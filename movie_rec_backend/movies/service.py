import requests
import logging
from django.conf import settings
from django.db import transaction


from .models import Movie

logger = logging.getLogger(__name__)


def fetch_and_save_trending_movies():
    """
    Fetches trending movies from the TMDb API and saves them to the database
    using atomic get_or_create for efficiency.
    """
    from .tasks import fetch_and_save_movie_details

    api_key = settings.TMDB_API_KEY
    base_url = "https://api.themoviedb.org/3/trending/movie/week"

    params = {
        'api_key': api_key,
        'language': 'en-US'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad response
        data = response.json()

        # Base image URL for posters
        img_base_url = "https://image.tmdb.org/t/p/w500"

        movies = data.get('results', [])

        with transaction.atomic():
            for movie_data in movies:
                third_party_id = movie_data.get('id')
                poster_path = movie_data.get('poster_path')

                poster_url = (
                    f"{img_base_url}{poster_path}"
                    if poster_path else None
                )

                movie, created = Movie.objects.get_or_create(
                    third_party_id=third_party_id,
                    defaults={
                        'title': movie_data.get('title'),
                        'poster_url': poster_url,
                        'release_date': movie_data.get('release_date')
                    }
                )

                if created:
                    logger.info(
                        f"Saved new movie: {movie.title} and enqueued detail "
                        f"fetch."
                    )
                    fetch_and_save_movie_details.delay(movie.pk)
                else:
                    logger.debug(
                        f"Movie already exists: {movie.title}"
                    )
        logger.info(f"Triggered detail fetch for movie: {movie.title}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from TMDb API: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
