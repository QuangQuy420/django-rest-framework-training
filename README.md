# Django REST Framework Blog API

A modular Django REST Framework project with authentication, blog posts, comments, reactions, Celery for async tasks, Redis, PostgreSQL, and JWT authentication using SimpleJWT.

---

## 1. How to Start the Application with Docker (Recommended for WSL or Linux environments)

### 1.1. Clone the project
```bash
git clone git@github.com:QuangQuy420/django-rest-framework-training.git
cd django-rest-framework-training
```

### 1.2. Configure .env (Edit if any)
```bash
cp .env.example .env
```

### 1.3. Build and Start
```bash
docker compose up --build
```

### 1.4. Apply Migrations
```bash
docker compose exec web python manage.py migrate
```

### 1.5. Create Superuser (Optional)
```bash
docker compose exec web python manage.py createsuperuser
```

### You can now access your API at http://localhost:8000

---

## 2. How to start application with Windows

### 2.1. Since you aren't using Docker images, you must install the software directly on your machine.
#### PostgreSQL:
- Download the PostgreSQL Installer for Windows.
- During installation, set the password to 123456 (to match your .env) or update your .env later.
- Open pgAdmin (installed with Postgres) or a terminal and create a database named drf_db.

#### Redis:
- Redis does not run natively on Windows.
- Option A (Recommended): Install Memurai (Developer Edition). It is a Redis-compatible cache for Windows.
- Option B: Download the archived Microsoft Redis port. (Note: This is very old/outdated but works for simple testing).

### 2.2. Clone the project
```bash
git clone git@github.com:QuangQuy420/django-rest-framework-training.git
cd django-rest-framework-training
```

### 2.3. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2.4. Install libraries: Important: You might need to install psycopg2-binary instead of psycopg2 on Windows to avoid build errors.
```bash
pip install -r requirements.txt
```

##### (If that fails on psycopg2, run pip install psycopg2-binary manually).

### 2.5. Configure .env (Edit if any)
```bash
cp .env.example .env
```

### 2.6. Run Migration
```bash
python manage.py migrate
```

### 2.7. Start Server
```bash
python manage.py runserver
```

### 2.8. Run Celery Worker (Critical Change) Celery's default execution pool (prefork) does not work on Windows. You must use the solo or threads pool.
```bash
# Add --pool=solo flag
celery -A config worker -l info --pool=solo
```

### You can now access your API at http://localhost:8000

---

## 3. Run Lint (Optional)
```bash
ruff check . --fix && ruff format .
```

---

## 4. Run Test (Optional)
```bash
pytest
```

---

## 5. Run Test Coverage (Optional)
```bash
pytest --cov=apps --cov-report=term-missing
```

---

## 6. Test API - Postman

### 6.1. Register/Sign In
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

### 6.2. Login to get token
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

### 6.3. Access protected endpoint
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

### 6.4. Refresh access token and rotate refresh token
```bash
POST /api/users/token/refresh/

Response:
{
  "access": "<access_token_here>"
}
```

### 6.5. Logout
```bash
POST /api/users/logout/
Header: Authorization: Bearer <access_token_here>

Response:
{
  "detail": "Logged out"
}
```

### 6.6. List all Post
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

### 6.7. Retrieve a Post
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

### 6.8. Create a Post
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

### 6.9. Update a Post (Full Update)
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

### 6.10. Partial Update a Post
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

### 6.11. Delete a Post
```bash
DELETE /api/blog/{id}/
Header: Authorization: Bearer <access_token>

Response: 204 No Content
```

### 6.12. List Comments of a Post
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

### 6.13. Create Comment for a Post
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

### 6.14. Update comment
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

### 6.15. List Reaction for a Post
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

### 6.16. Create Reaction for a Post
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

### 6.17. List Reaction for a Comment
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

### 6.18. Create Reaction for a Comment
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

### 6.19. Update Reaction Type
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

### 6.20. Delete Reaction
```bash
DELETE /api/blog/reactions/{reaction_id}/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "content": "Updated comment text"
}

Response: 204 No Content
```