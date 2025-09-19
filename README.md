# Project Nexus Documentation

## Overview

This repository, **alx-project-nexus**, is a documentation hub for my major learnings from the ProDev Backend Engineering program. It serves as a knowledge base, showcasing my understanding of key backend engineering concepts, tools, and best practices.

## Project Objectives

* **Consolidate Key Learnings:** To document and consolidate key learnings from the ProDev Backend Engineering program.
* **Create a Reference Guide:** To serve as a comprehensive guide for both current and future learners.
* **Foster Collaboration:** To encourage and facilitate collaboration between backend and frontend learners.

---

### Featured Project: Movie Recommendation Backend

#### **Overview**

This project focuses on developing a robust backend for a movie recommendation application. The backend provides APIs for retrieving trending and recommended movies, user authentication, saving user preferences, and facilitating user interaction through comments and likes. It emphasizes performance optimization and comprehensive API documentation.

#### **Project Goals**

* **API Creation:** Develop endpoints for fetching trending and recommended movies from a third-party API.
* **User Management:** Implement user authentication using JWT and allow users to save their favorite movies.
* **User Interaction:** Create a system for users to add **comments** and **likes** to movies.
* **Performance Optimization:** Use Redis for caching to improve API response times and leverage asynchronous tasks for long-running operations.
* **Comprehensive Documentation:** Document all API endpoints using Swagger.

#### **Technologies Used**

* **Backend Framework:** Django
* **Database:** PostgreSQL
* **Caching:** Redis
* **Asynchronous Tasks:** Celery & RabbitMQ
* **API Documentation:** Swagger

---

### Major Learnings

#### **Key Technologies Covered**

* **Python:** A versatile language used for developing robust backend systems.
* **Django:** A high-level Python web framework that encourages rapid development and clean design.
* **REST APIs:** An architectural style for designing networked applications.
* **Message Queues:** A form of asynchronous service-to-service communication used in serverless and microservices architectures.
* **Celery & RabbitMQ:** A distributed task queue and its message broker, used for executing long-running tasks asynchronously.

#### **Important Backend Development Concepts**

* **Database Design:** Principles for structuring and organizing data in a database.
* **Asynchronous Programming:** Techniques for handling multiple tasks simultaneously without blocking execution.
* **Caching Strategies:** Methods for storing frequently accessed data to improve performance.
* **System Design:** [My explanation here]

---

### Challenges and Solutions

This section will document real-world challenges faced during the project and the solutions implemented.

* **PostgreSQL Connection Issue:**
  * **Challenge:** The Django application failed to connect to the PostgreSQL database, which was listening on a non-default port (`5323`) rather than the expected default (`5432`).
  * **Solution:** The .env configuration file (`.env`) was edited to change the `port` setting from `5323` to `5432`. After this correction, the database connection was successfully established, and Django migrations were applied. This highlighted the importance of matching application database settings with the server's configuration.

* **Django REST Framework Template Error:**
  * **Challenge:** The browsable API returned a `TemplateDoesNotExist` error when attempting to render `rest_framework/api.html`, preventing the API from being viewed in the browser. 
  * **Solution:** This was resolved by adding `'rest_framework'` to the `INSTALLED_APPS` list in `settings.py`. This ensures that Django can locate and use the necessary templates and other components provided by the DRF library.

* **Django REST Framework Router Basename Error:**
  * **Challenge:** The `DefaultRouter` in `urls.py` raised an `AssertionError` because it couldn't automatically determine the `basename` for viewsets that lacked a `queryset` attribute.
  * **Solution:** The `basename` was explicitly defined for each viewset registration in `urls.py` (`router.register(r'favorites', FavoriteMovieViewSet, basename='favorite')`). This provided the router with the necessary information to generate the correct URL patterns.

---

### Best Practices and Personal Takeaways

This section highlights industry best practices, personal insights, and key takeaways from the project.

* **[Best Practice 1]:** [My insight or takeaway].

---

### Database Schema

This diagram provides a visual representation of the database models and their relationships, including tables for users, movies, favorites, comments, and likes.

[Image of the database schema](movie_rec_backend/docs/db-schema.png)
