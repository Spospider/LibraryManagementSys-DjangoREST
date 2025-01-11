# Library Management System with Celery Integration

## Overview
This project is a Library Management System built using Django and integrated with Celery for background task processing. The application supports user registration and authentication, library and book browsing, borrowing and returning books, and asynchronous tasks like sending emails. The system also integrates Celery for managing background tasks such as sending welcome emails or processing book-related operations asynchronously.

## Key Features

- **User Authentication:**
  - Registration: Users can register with a username, password, email, and location.
  - Login: Users can log in using their credentials to receive an access token for subsequent requests.

- **Library and Book Management:**
  - Users can browse available libraries, authors, and books.
  - Book borrowing: Users can borrow books from the library (with a maximum borrowing limit and duration).
  - Book returning: Users can return borrowed books, triggering background tasks (e.g., updating stock).

- **Celery Integration:**
  - Celery is integrated to handle background tasks, such as sending welcome emails to users after registration.
  - During testing, Celery tasks are executed synchronously (in-memory) to facilitate testing without requiring a real broker or worker.

## Key Technologies Used

- **Django**: Used as the web framework for building the API.
- **Django Rest Framework (DRF)**: Used to build RESTful APIs for user interactions.
- **Celery**: Used for handling background tasks asynchronously.
- **Redis**: Used as the message broker for Celery.
- **PostgreSQL**: Database for storing user, book, and library information (configured in settings).
- **pytest/Django TestCase**: Used to write tests for the application, including verifying Celery functionality.

## Setup Instructions

### 1. Install Dependencies
Make sure you have Python 3.8+ installed, and install the required dependencies using:

```bash
pip install -r requirements.txt
```

```bash
# If you're using Redis on a local machine:
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu
redis-server  # Start Redis server
```

configuring celery broker settings
```
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

ORM migrations
```
python manage.py makemigrations
python manage.py migrate
```

running the Celery Worker:
```bash
celery -A your_project worker --loglevel=info
```
Running the server:
```bash
python manage.py runserver
```

Running tests: (some testcases need celery)
```bash
python manage.py test
```

## API Endpoints

### User Authentication
	•	POST /api/register/: Register a new user.
	•	POST /api/login/: Log in with a username and password to receive a JWT access token.

### Library Management
	•	GET /api/libraries/: List all libraries.
	•	GET /api/authors/: List all authors.
	•	GET /api/books/: List all books.

### Book Borrowing and Returning
	•	POST /api/borrow/: Borrow a book (requires an authenticated user).
	•	POST /api/return/: Return a borrowed book (requires an authenticated user).

### Celery Tasks
	•	Background tasks, such as sending emails, are handled asynchronously using Celery. You can test task execution by calling them directly in test cases, like user registration.

## TODO 
Create docker compose for easier testing, (celery + redis + django)