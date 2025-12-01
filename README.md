## Create environment
```bash
python -m venv .venv
source .venv/bin/activate
```

## Create Django project inside "config" package
```bash
django-admin startproject config .
```

## Freeze requirements
```bash
pip freeze > requirements.txt
```

## Create folder in apps/ directory
```bash
python manage.py startapp users apps/users
python manage.py startapp blog apps/blog
python manage.py startapp notifications apps/notifications
python manage.py startapp api apps/api
python manage.py startapp core apps/core
```

## Start Postgres
```bash
docker compose up -d
```

## Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Run the Development Server
```bash
python manage.py runserver
```

## Create superuser
```bash
python manage.py createsuperuser
```

## Test API
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

Response:
{
  "detail": "Post deleted successfully"
}
```