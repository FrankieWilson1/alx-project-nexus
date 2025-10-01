# Project Nexus Documentation

## Overview

This repository, `alx-project-nexus`, is a documentation hub for my major learnings from the ProDev Backend Engineering program. It serves as a knowledge base, showcasing my understanding of key backend engineering concepts, tools, and best practices.

## Project Objectives

- **Consolidate Key Learnings**: To document and consolidate key learnings from the ProDev Backend Engineering program.
- **Create a Reference Guide**: To serve as a comprehensive guide for both current and future learners.
- **Foster Collaboration**: To encourage and facilitate collaboration between backend and frontend learners.

## Featured Project: Movie Recommendation Backend

### Overview

This project focuses on developing a robust backend for a movie recommendation application. The backend provides APIs for retrieving trending and recommended movies, user authentication, saving user preferences, and facilitating user interaction through comments and likes. It emphasizes performance optimization and comprehensive API documentation.

### Project Goals

- **API Creation**: Develop endpoints for fetching trending and recommended movies from a third-party API.
- **User Management**: Implement user authentication using JWT and allow users to save their favorite movies.
- **User Interaction**: Create a system for users to add comments and likes to movies.
- **Performance Optimization**: Use Redis for caching to improve API response times and leverage asynchronous tasks for long-running operations.
- **Comprehensive Documentation**: Document all API endpoints using Swagger.

### Technologies Used

- **Backend Framework**: Django
- **Database**: PostgreSQL
- **Caching**: Redis
- **Asynchronous Tasks**: Celery & RabbitMQ (Note: Core detail-fetching switched to synchronous for deployment on free tier.)
- **API Documentation**: Swagger

## 🚀 API Endpoints

The API is served from the base URL: `https://alx-project-nexus-jdbi.onrender.com/api/`. Endpoints requiring authentication must include a valid JWT Access Token in the `Authorization: Bearer <token>` header.

### 1. Authentication & User Endpoints

| Full Path              | Method | Protection       | Description                                      |
|------------------------|--------|------------------|--------------------------------------------------|
| `/api/register/`      | POST   | Public (AllowAny) | Creates a new user account.                       |
| `/api/token/`         | POST   | Public (AllowAny) | Obtains JWT access and refresh tokens (using username/password). |
| `/api/token/refresh/` | POST   | Public (AllowAny) | Refreshes an expired access token using the refresh token. |
| `/api/profile/`       | GET    | Protected (IsAuthenticated) | Retrieves the authenticated user's profile details. |

### 2. Movie Data & Discovery Endpoints

| Full Path                                         | Method | Protection                     | Description                                         | Query/Path Params        |
|---------------------------------------------------|--------|--------------------------------|-----------------------------------------------------|---------------------------|
| `/api/movies/`                                   | GET    | Partial (IsAuthenticatedOrReadOnly) | Retrieves a paginated list of movies (defaults to trending). | `?page=...`              |
| `/api/movies/{id}/`                              | GET    | Partial (IsAuthenticatedOrReadOnly) | Retrieves details for a single movie.               | `{id} : Movie ID`        |
| `/api/movies/{movie_id}/recommendations/`       | GET    | Protected (IsAuthenticated)    | Lists all stored recommendations for a movie, paginated. | `{movie_id} : Source Movie ID` |
| `/api/movies/{movie_id}/recommendations/trigger/`| POST   | Protected (IsAuthenticated)    | Triggers the fetch process to find and save new recommendations (runs synchronously now). | `{movie_id} : Source Movie ID` |

#### Example Movie Object (Expected Result)

```json
{
  "id": 1,
  "title": "The Fantastic 4: First Steps",
  "third_party_id": 617126,
  "poster_url": "https://image.tmdb.org/t/p/w500/...",
  "release_date": "2025-07-22",
  "overview": "A detailed plot summary...", // ✅ Populated
  "duration_minutes": 120, // ✅ Populated
  "genres": ["Action", "Adventure"], // ✅ Populated
  "cast": ["Actor Name 1", "Actor Name 2"], // ✅ Populated
  "total_likes": 0,
  "total_comments": 0
}
```

### 3. User Interaction Endpoints (Protected)

These viewsets (favorites, comments, likes) inherit from `BaseUserObjectViewSet`, meaning they automatically filter results to the authenticated user and require an authenticated user for creation/deletion.

| Full Path              | Method | Description                                          | Request Body                               | Query Parameters                   |
|------------------------|--------|------------------------------------------------------|-------------------------------------------|------------------------------------|
| `/api/favorites/`     | GET    | Lists the authenticated user's favorite movies.      | N/A                                       | N/A                                |
| `/api/favorites/`     | POST   | Adds a movie to favorites.                           | `{"movie": 1}` (Movie PK)               | N/A                                |
| `/api/favorites/{id}/`| DELETE | Removes a specific favorite entry.                   | N/A                                       | `{id} : FavoriteMovie PK`         |
| `/api/comments/`      | GET    | Lists comments. Defaults to user's, but can be filtered. | N/A                                       | `?movie=1` (To list all comments for Movie PK 1) |
| `/api/comments/`      | POST   | Posts a new comment.                                 | `{"movie": 1, "content": "Great!"}`     | N/A                                |
| `/api/comments/{id}/` | DELETE | Deletes the user's comment entry.                    | N/A                                       | `{id} : Comment PK`               |
| `/api/likes/`         | GET    | Lists the authenticated user's likes.                | N/A                                       | N/A                                |
| `/api/likes/`         | POST   | Adds a like for a movie.                             | `{"movie": 1}` (Movie PK)                | N/A                                |
| `/api/likes/{id}/`    | DELETE | Removes a specific like entry.                       | N/A                                       | `{id} : Like PK`                  |

## Major Learnings

### Key Technologies Covered

- **Python**: A versatile language used for developing robust backend systems.
- **Django**: A high-level Python web framework that encourages rapid development and clean design.
- **REST APIs**: An architectural style for designing networked applications.
- **Message Queues**: A form of asynchronous service-to-service communication used in serverless and microservices architectures.
- **Celery & RabbitMQ**: A distributed task queue and its message broker, used for executing long-running tasks asynchronously.

### Important Backend Development Concepts

- **Database Design**: Principles for structuring and organizing data in a database.
- **Asynchronous Programming**: Techniques for handling multiple tasks simultaneously without blocking execution.
- **Caching Strategies**: Methods for storing frequently accessed data to improve performance.
- **System Design**: [My explanation here]

## Challenges and Solutions

This section will document real-world challenges faced during the project and the solutions implemented.

- **PostgreSQL Connection Issue**:
  - **Challenge**: The Django application failed to connect to the PostgreSQL database, which was listening on a non-default port (5323) rather than the expected default (5432).
  - **Solution**: The `.env` configuration file was edited to change the port setting from 5323 to 5432. After this correction, the database connection was successfully established, and Django migrations were applied. This highlighted the importance of matching application database settings with the server's configuration.

- **Django REST Framework Template Error**:
  - **Challenge**: The browsable API returned a `TemplateDoesNotExist` error when attempting to render `rest_framework/api.html`, preventing the API from being viewed in the browser.
  - **Solution**: This was resolved by adding 'rest_framework' to the `INSTALLED_APPS` list in `settings.py`. This ensures that Django can locate and use the necessary templates and other components provided by the DRF library.

- **Django REST Framework Router Basename Error**:
  - **Challenge**: The `DefaultRouter` in `urls.py` raised an `AssertionError` because it couldn't automatically determine the basename for viewsets that lacked a queryset attribute.
  - **Solution**: The basename was explicitly defined for each viewset registration in `urls.py` (e.g., `router.register(r'favorites', FavoriteMovieViewSet, basename='favorite')`). This provided the router with the necessary information to generate the correct URL patterns.

- **Asynchronous Task Failure (The Final Fix)**:
  - **Challenge**: Movie detail fields (overview, genres, cast) remained null because the Celery worker, intended to run the asynchronous fetching tasks, could not be deployed on the Render free tier.
  - **Solution**: The data pipeline was redesigned to perform the detail fetching synchronously. The call to `fetch_and_save_movie_details.delay(...)` was replaced with a direct function call (`fetch_and_save_movie_details(...)`) within the `fetch_movies` management command, ensuring all data population occurs reliably during the deployment build process.

## Best Practices and Personal Takeaways

This section highlights industry best practices, personal insights, and key takeaways from the project.

- **Code Quality and Standards (Pycodestyle)**:
  - **Takeaway**: Adhering to standards like PEP 8 and enforcing them with tools like Pycodestyle (and flake8) is crucial for collaboration and long-term maintenance. It establishes consistency, making the codebase easier to read, review, and debug.

- **Asynchronous vs. Synchronous Execution**:
  - **Takeaway**: While asynchronous workers (Celery) are best practice for production systems to avoid blocking the main web server, they incur infrastructure costs (separate worker service). For lightweight tasks or free-tier deployments, integrating long-running tasks into scheduled synchronous management commands during the build/deploy cycle is a viable, cost-effective workaround.

- **Custom Base ViewSets for Authorization**:
  - **Takeaway**: Creating a reusable `BaseUserObjectViewSet` with methods like `perform_create` (to set the user) and `get_queryset` (to filter by user) drastically simplifies the implementation of protected, user-owned resources like Favorites, Comments, and Likes, ensuring strong, consistent access control.


---

### Database Schema

This diagram provides a visual representation of the database models and their relationships, including tables for users, movies, favorites, comments, and likes.

[Image of the database schema](https://dbdiagram.io/d/alx_movie_recommendation_model-68c5ed10841b2935a66e3e42)
