from django.core.management.base import BaseCommand

from movies.service import fetch_and_save_trending_movies


class Command(BaseCommand):
    """
    Django command to fetch trending movies from TMDb APII
    """
    help = 'Fetches trending movies and saves them to the database.'

    def handle(self, *args, **options):
        self.stdout.write("Starting to fetch movies...")
        try:
            fetch_and_save_trending_movies()
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully fetched and saved movies.'
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred: {e}'))
