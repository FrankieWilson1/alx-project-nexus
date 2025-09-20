import requests
from django.conf import settings

from .models import Movie


def fetch_and_save_trending_movies():
    """
    Fetches trending movies from the TMDb API and saves them to the database
    """
    api_key = settings.TMDB_API_KEY
    base_url = "https://api.themoviedb.org/3/trending/movie/week?"

    try:
        response = requests.get(base_url, params={'api_key': api_key})
        response.raise_for_status()  # Raises an HTTPError for bad response
        data = response.json()
        img_url = "https://image.tmdb.org/t/p/w500"

        movies = data.get('results', [])

        for movie_data in movies:
            third_party_id = movie_data.get('id')
            # Checks if the movie already exists in the database
            if not Movie.objects.filter(
                third_party_id=third_party_id
            ).exists():
                Movie.objects.create(
                    title=movie_data.get('title'),
                    third_party_id=third_party_id,
                    poster_url=f"{img_url}{movie_data.get('poster_path')}",
                    release_date=movie_data.get('release_date')
                )
                print(f"Saved new movie: {movie_data.get('title')}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from TMDb API: {e}")
