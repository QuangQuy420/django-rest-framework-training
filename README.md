# Django REST Framework Blog API

A modular Django REST Framework project with authentication, blog posts, comments, reactions, Celery for async tasks, Redis, PostgreSQL, and JWT authentication using SimpleJWT.

==============================================================

## How to Start the Application with Docker (Recommended for WSL or Linux environments)
### Configure .env (Edit if any)
```bash
cp .env.example .env
```

### Build and Start
```bash
docker compose up --build
```

### Apply Migrations
```bash
docker compose exec web python manage.py migrate
```

### Create Superuser (Optional)
```bash
docker compose exec web python manage.py createsuperuser
```

### You can now access your API at http://localhost:8000

==============================================================

## How to start application with Windows
### Since you aren't using Docker images, you must install the software directly on your machine.
#### - PostgreSQL:
##### + Download the PostgreSQL Installer for Windows.
##### + During installation, set the password to 123456 (to match your .env) or update your .env later.
##### + Open pgAdmin (installed with Postgres) or a terminal and create a database named drf_db.

#### - Redis:
##### + Redis does not run natively on Windows.
##### + Option A (Recommended): Install Memurai (Developer Edition). It is a Redis-compatible cache for Windows.
##### + Option B: Download the archived Microsoft Redis port. (Note: This is very old/outdated but works for simple testing).

### Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

### Install libraries: Important: You might need to install psycopg2-binary instead of psycopg2 on Windows to avoid build errors.
```bash
pip install -r requirements.txt
```

##### (If that fails on psycopg2, run pip install psycopg2-binary manually).

### Configure .env (Edit if any)
```bash
cp .env.example .env
```

### Run Migration
```bash
python manage.py migrate
```

### Start Server
```bash
python manage.py runserver
```

### Run Celery Worker (Critical Change) Celery's default execution pool (prefork) does not work on Windows. You must use the solo or threads pool.
```bash
# Add --pool=solo flag
celery -A config worker -l info --pool=solo
```

### You can now access your API at http://localhost:8000

==============================================================

## (Optional)
## Run Lint
```bash
ruff check . --fix && ruff format .
```

## Run Test
```bash
pytest
```

## Run Test Coverage
```bash
pytest --cov=apps --cov-report=term-missing
```

==============================================================

# Test API - Postman
### Register/Sign In
```bash
POST /api/users/register/
Body:
{
  "username": "quy",
  "email": "quy@example.com",
  "password": "secret123"
}

Response:
{
    "id": 2,
    "username": "quy",
    "email": "quy@example.com"
}
```
### Login to get token
```bash
POST /api/users/login/
Body:
{
  "username": "quy",
  "password": "secret123"
}

Response:
{
  "access": "<access_token_here>"
}
```
### Access protected endpoint
```bash
GET /api/users/me/
Header: Authorization: Bearer <access_token_here>

Response:
{
    "id": 2,
    "username": "quy1",
    "email": "quy1@example.com",
    "first_name": "",
    "last_name": ""
}
```
### Refresh access token and rotate refresh token
```bash
POST /api/users/token/refresh/

Response:
{
  "access": "<access_token_here>"
}
```
### Logout
```bash
POST /api/users/logout/
Header: Authorization: Bearer <access_token_here>

Response:
{
  "detail": "Logged out"
}
```
### List all Post
```bash
GET /api/blog/
Header: Authorization: Bearer <access_token>

Response:
{
  "count": 42,
  "next": "http://localhost:8000/api/blog/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Hello",
      "content": "World",
      "created_at": "...",
      "updated_at": "...",
      "author": { ... },
      "reactions": [ ... ],
      "comments": [ ... ]
    }
  ]
}

```
### Retrieve a Post
```bash
GET /api/blog/{id}/
Header: Authorization: Bearer <access_token>

Response:
{
  "id": 1,
  "title": "Hello",
  "content": "World",
  "created_at": "...",
  "updated_at": "...",
  "author": { ... },
  "reactions": [ ... ],
  "comments": [ ... ]
}
```
### Create a Post
```bash
POST /api/blog/
Header: Authorization: Bearer <access_token>

Body:
{
  "title": "My first post",
  "content": "This is my content"
}

Response:
{
  "id": 10,
  "title": "My first post",
  "content": "This is my content",
  "created_at": "...",
  "updated_at": "...",
  "author": { ... },
  "reactions": [],
  "comments": []
}
```
### Update a Post (Full Update)
```bash
PUT /api/blog/{id}/
Header: Authorization: Bearer <access_token>

Body:
{
  "title": "Updated title",
  "content": "Updated content"
}

Response:
{
  "id": 10,
  "title": "Updated title",
  "content": "Updated content",
  "created_at": "...",
  "updated_at": "...",
  "author": { ... },
  "reactions": [...],
  "comments": [...]
}
```
### Partial Update a Post
```bash
PATCH /api/blog/{id}/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "title": "Only title changed"
}

Response:
{
  "id": 10,
  "title": "Updated title",
  "content": "Updated content",
  "created_at": "...",
  "updated_at": "...",
  "author": { ... },
  "reactions": [...],
  "comments": [...]
}
```
### Delete a Post
```bash
DELETE /api/blog/{id}/
Header: Authorization: Bearer <access_token>

Response: 204 No Content
```
### List Comments of a Post
```bash
GET /api/blog/{post_id}/comments/
Header: Authorization: Bearer <access_token>

Response:
[
  {
    "id": 10,
    "content": "Great article!",
    "created_at": "2025-01-20T08:15:00Z",
    "author": {
      "id": 5,
      "username": "john"
    },
    "reactions": [],
    "replies": [],
    "parent": null,
    "post": 3
  }
]
```
### Create Comment for a Post
```bash
POST /api/blog/{post_id}/comments/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "content": "This is my comment.",
  "parent": null/post_id
}

Response:
{
  "id": 16,
  "content": "This is my comment.",
  "created_at": "2025-01-20T08:31:00Z",
  "author": {
    "id": 1,
    "username": "quyphan"
  },
  "reactions": [],
  "replies": [],
  "parent": 10/null,
  "post": 3
}
```
### Update comment
```bash
PATCH /api/blog/comments/{id}/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "content": "Updated comment text"
}

Response:
{
  "id": 10,
  "content": "Updated comment text",
  "created_at": "...",
  "author": {
    "id": 1,
    "username": "quyphan"
  },
  "reactions": [],
  "replies": [],
  "parent": null,
  "post": 3
}
```
### List Reaction for a Post
```bash
GET /api/blog/{post_id}/reactions/
Header: Authorization: Bearer <access_token>

Response:
[
  {
    "id": 5,
    "type": "like",
    "created_at": "2025-01-20T10:00:00Z",
    "user": {
      "id": 2,
      "username": "john"
    }
  },
  {
    "id": 6,
    "type": "LOVE",
    "created_at": "2025-01-20T10:10:00Z",
    "user": {
      "id": 3,
      "username": "anna"
    }
  }
]
```
### Create Reaction for a Post
```bash
POST /api/blog/{post_id}/reactions/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "type": "like"
}

Response:
{
    "id": 1,
    "type": "haha",
    "created_at": "2025-12-02T01:57:56.917934Z",
    "author": {
        "id": 1,
        "username": "quy",
        "email": "quy@gmail.com",
        "first_name": "",
        "last_name": ""
    }
}
```
### List Reaction for a Comment
```bash
GET /api/blog/comments/{comment_id}/reactions/
Header: Authorization: Bearer <access_token>

Response:
[
  {
    "id": 5,
    "type": "like",
    "created_at": "2025-01-20T10:00:00Z",
    "user": {
      "id": 2,
      "username": "john"
    }
  },
  {
    "id": 6,
    "type": "LOVE",
    "created_at": "2025-01-20T10:10:00Z",
    "user": {
      "id": 3,
      "username": "anna"
    }
  }
]
```
### Create Reaction for a Comment
```bash
POST /api/blog/comments/{comment_id}/reactions/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "type": "like"
}

Response:
{
    "id": 1,
    "type": "haha",
    "created_at": "2025-12-02T01:57:56.917934Z",
    "author": {
        "id": 1,
        "username": "quy",
        "email": "quy@gmail.com",
        "first_name": "",
        "last_name": ""
    }
}
```
### Update Reaction Type
```bash
PATCH /api/blog/reactions/{reaction_id}/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "type": "haha"
}

Response:
{
    "id": 3,
    "type": "like",
    "created_at": "2025-12-01T10:44:36.114361Z",
    "author": {
        "id": 1,
        "username": "quy",
        "email": "quy@gmail.com",
        "first_name": "",
        "last_name": ""
    }
}
```
### Delete Reaction
```bash
DELETE /api/blog/reactions/{reaction_id}/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "content": "Updated comment text"
}

Response: 204 No Content
```