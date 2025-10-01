#!/usr/bin/env bash
set -e

pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate

python manage.py shell -c "from movies.models import Movie; Movie.objects.all().delete()"

python manage.py fetch_movies
