from celery import shared_task
import requests
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max

from .service import fetch_and_save_trending_movies as core_fetcher
from .models import (
    Movie,
    Recommendation,
    Genre,
    CastMember,
    PersonalizedRecommendation
)

logger = logging.getLogger(__name__)

# Constants variables
TMDB_IMG_BASE_URL = "https://image.tmdb.org/t/p/w500/"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"


@shared_task
def fetch_and_save_trending_movies():
    """
    Celery Beat periodic task that fetches trending movies
    and enqueues detail fetching tasks.
    """
    logger.info(
        "Celery Beat has started the periodic movie fetch."
    )
    core_fetcher()

    logger.info(
        "Periodic movie fetch complete. Details tasks should now be enqueued."
    )

    return (
        "Successfully processed tasks"
    )


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=5
)
@transaction.atomic
def fetch_and_save_movie_details(self, movie_pk: int):
    """
    Helper function to fetch detailed data (overview, runtime, genres, cast)
    and update the Movie object.
    """
    api_key = settings.TMDB_API_KEY

    try:
        movie = Movie.objects.select_for_update().get(pk=movie_pk)
    except Movie.DoesNotExist as e:
        logger.warning(
            f"Movie with PK {movie_pk} not found"
        )
        raise self.retry(exc=e, countdown=self.default_retry_delay)

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
        movie.rating = details_data.get('vote_average')

        genre_names = (
            [g.get('name') for g in details_data.get('genres', [])]
        )

        genre_objects = []
        for name in genre_names:
            genre, _ = Genre.objects.get_or_create(name=name)
            genre_objects.append(genre)

        movie.genres.set(genre_objects)

    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching details for TMDb ID {tmdb_id}: {e}")
        raise self.retry(exc=e, countdown=self.default_retry_delay)

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

        cast_member_objects = []
        for member_data in cast_list:
            cast_name = member_data.get('name')
            if cast_name:
                cast_member, _ = CastMember.objects.get_or_create(
                    name=cast_name
                )
                cast_member_objects.append(cast_member)

        movie.cast.set(cast_member_objects)

        logger.info(
            f"Updated genres and cast for movie: "
            f"{movie.title}"
        )

    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching credits for TMDb ID {tmdb_id}: {e}")
        raise self.retry(exc=e, countdown=self.default_retry_delay)

    movie.save()


@shared_task
@transaction.atomic  # Ensures all DB operations
def fetch_and_save_recommendations(local_movie_pk):
    """
    Fetches and saves item-to-item recommended movies for a given local
    movie PK, and populates details for all newly added movies.
    """
    api_key = settings.TMDB_API_KEY

    try:
        source_movie = Movie.objects.select_for_update().get(pk=local_movie_pk)

        # If the source movie is just a placeholder, fetch its details now.
        if not source_movie.overview or not source_movie.genres.exists():
            fetch_and_save_movie_details.delay(source_movie.pk)

        tmdb_movie_id = source_movie.third_party_id
        url = f"{TMDB_BASE_URL}{tmdb_movie_id}/recommendations"

        logger.info(
            f"Querying TMDb for recommendations using external ID: -> "
            f"{tmdb_movie_id}"
        )
        response = requests.get(url, params={'api_key': api_key})
        response.raise_for_status()
        data = response.json()

        recommended_movies_data = data.get('results', [])

        if not recommended_movies_data:
            logger.info(
                f"No recommendations found for movie ID: "
                f"{tmdb_movie_id}."
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
                fetch_and_save_movie_details.delay(recommended_movie.pk)

            if created:
                logger.info(
                    f"Saved new recommended movie: {recommended_movie.title}"
                )

            Recommendation.objects.update_or_create(
                source_movie=source_movie,
                recommended_movie=recommended_movie,
                defaults={'score': movie_data.get('vote_average', 0)}
            )
            logger.info(
                f"Created recommendation link: {source_movie.title} -> "
                f"{recommended_movie.title}"
            )

    except Movie.DoesNotExist:
        logger.error(
            f"Source movie with local PK {local_movie_pk}"
            f" does not exist locally."
        )
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching recommendations from TMDb: {e}")


@shared_task
def calculate_personalized_recommendations_for_all():
    """
    Celery Beat periodic task that triggers personalized recommendation
    calculation for all active users.
    """
    User = get_user_model()
    users = User.objects.filter(is_active=True)

    for user in users:
        calculate_personalized_recommendations_for_user.delay(user.pk)
    logger.info(
        f"Enqueued calculation jobs for {users.count()} users."
    )
    return f"Successfully enqueued tasks for {users.count()} users."


@shared_task
@transaction.atomic
def calculate_personalized_recommendations_for_user(user_pk: int):
    """
    Calculates and saves personalized recommendations for a single user
    based on liked moves.
    """
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        logger.warning(
            f"User with PK {user_pk} not found. Skipping calculation."
        )
        return

    # Get all movie IDs the user has liked
    liked_movie_ids = user.like_set.values_list(
        'movie_id',
        flat=True
    )

    if not liked_movie_ids:
        logger.info(
            f"User {user.username} has no liked movies. "
            f"Skipping recoomendations"
        )
        return

    # Get item-to-item recommendations for all liked movies:
    #   first -> Filters Recommendations where source_movie is one
    #               the user liked
    #   secondly -> Excludes recommendations that point back to a movie the
    #               user already liked.
    #   thirdly ->  Grouped by recommended_movie and take the MAX score (to
    #               represent the best match)
    all_recs_queryset = Recommendation.objects.filter(
        source_movie_id__in=liked_movie_ids
    ).exclude(
        recommended_movie__in=liked_movie_ids
    ).values(
        'recommended_movie_id'
    ).annotate(
        avg_score=Max('score')
    ).order_by('-avg_score')[:20]

    # Clear old personalized recs for a fresh list
    PersonalizedRecommendation.objects.filter(user=user).delete()

    # Prepare list for bulk creation
    new_recs_list = [
        PersonalizedRecommendation(
            user=user,
            recommended_movie_id=rec['recommended_movie_id'],
            score=rec['avg_score']
        )
        for rec in all_recs_queryset
    ]

    PersonalizedRecommendation.objects.bulk_create(new_recs_list)
    new_recs_count = len(new_recs_list)

    logger.info(
        f"Calculated and saved {new_recs_count} persornalized "
        f"recommendations for user {user.username}"
    )


@shared_task
def generate_all_item_to_item_rec():
    """
    Triggers the item-to-item recommendation generation task for all existing
    movies
    """
    logger.info("Starting Item-to-Item recommendation generation.")

    movie_pks = Movie.objects.values_list('pk', flat=True)

    for pk in movie_pks:
        fetch_and_save_recommendations.delay(pk)

    logger.info(
        f"Enqueued Item-to-Item generation for {len(movie_pks)} movies."
    )
    return "Successfully enqueued Item-to-Item recommendation tasks."
