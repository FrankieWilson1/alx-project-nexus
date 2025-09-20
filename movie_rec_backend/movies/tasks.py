from celery import shared_task
import requests
from django.conf import settings

from .models import Movie


@shared_task
def fetch_and_save_recommendations(movie_id):
    """
    Fetches and saves recommended movies for a given movie ID.
    This task is designed to be run asynchronously.
    """
    api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"

    try:
        response = requests.get(url, params={'api_key': api_key})
        response.raise_for_status()
        data = response.json()
        img_url = "https://image.tmdb.org/t/p/w500/"
        std_out_msg = "Saved recommended movie:"

        recommended_movies = data.get('results', [])

        for movide_data in recommended_movies:
            # Creat or recommend movie is created in database
            third_party_id = movide_data.get('id')
            if not Movie.objects.filter(
                third_party_id=third_party_id
            ).exists():
                Movie.objects.create(
                    title=movide_data.get('title'),
                    third_party_id=third_party_id,
                    poster_url=f"{img_url}{movide_data.get('poster_path')}",
                    release_date=movide_data.get('release_date')
                )
                print(
                    f"{std_out_msg} {movide_data.get('title')}"
                )
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recommendations: {e}")
