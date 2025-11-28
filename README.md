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