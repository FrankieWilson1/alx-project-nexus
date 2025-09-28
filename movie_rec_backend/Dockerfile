FROM python:3.11-slim

# 1. ROOT ACTIONS: Install System Dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
           build-essential \
           libpq-dev \
           netcat-openbsd \
           postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Directory and User (Still as root)
WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# CRITICAL FIX: Explicitly set the home directory for the appuser.
ENV HOME=/app

# Copy ALL files (as root)
COPY requirements.txt /app/
COPY . /app/

COPY wait-for-db.sh /usr/local/bin/

# Make the script executable
RUN chmod +x /usr/local/bin/wait-for-db.sh

# CRITICAL FIX: Transfer ownership of ALL files to the non-root user
RUN chown -R appuser:appgroup /app

# --- SWITCH TO UNPRIVILEGED USER ---
USER appuser

# Install Dependencies (Should now work as HOME=/app)
RUN pip install --no-cache-dir -r requirements.txt

# Set core environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=movie_rec_project.settings

# --- CRITICAL ENVIRONMENT FIXES ---

# 1. Fix for 'celery: not found' and 'django-admin' (Shell PATH)
# FIXED: Closed the quote and added the full path definition.
ENV PATH="/app/.local/bin:$PATH" 

# 2. Fix for 'No module named django' (Python Runtime PATH)
# ADDED: This directs Python to the custom installation directory for libraries.
ENV PYTHONPATH="/app/.local/lib/python3.11/site-packages:$PYTHONPATH"

# Define the entry point/default command
CMD ["gunicorn", "movie_rec_project.wsgi:application", "--bind", "0.0.0.0:8000"]

