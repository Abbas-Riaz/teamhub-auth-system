# TeamHub Auth System

TeamHub Auth System is a Django REST Framework backend for user authentication, email verification, password reset, organizations, memberships, and organization invitations.

## Features

- Custom user model with unique email login
- User registration with email verification
- JWT login using `djangorestframework-simplejwt`
- Forgot/reset password flow
- Organization create, list, detail, update, and delete APIs
- Organization membership roles: `owner`, `admin`, `member`, `viewer`
- Invite users to organizations
- Accept or decline pending invitations
- Celery support for async/background tasks
- Redis cache support with local-memory fallback

## Tech Stack

- Python 3.11.5
- Django 5.2
- Django REST Framework
- Simple JWT
- Celery
- django-celery-results
- django-celery-beat
- Redis optional
- SQLite for local development

## Project Structure

```text
teamhub-auth-system/
|-- accounts/          # Custom user model and account tasks
|-- authentication/    # Register, login, email verification, password reset
|-- organizations/     # Organizations, memberships, invitations
|-- teamhub/           # Django project settings and root URLs
|-- api.http           # Example API requests
|-- manage.py
|-- requirements.txt
|-- runtime.txt
`-- build.sh
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv env
env\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The current settings also import these packages, so install them if they are not already present:

```bash
pip install python-decouple dj-database-url whitenoise
```

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Run migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Base local API URL:

```text
http://127.0.0.1:8000/api
```

## Authentication APIs

Register a user:

```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass@123",
  "password2": "StrongPass@123"
}
```

Verify email:

```http
GET /api/auth/verify-email/?token=<email-token>
```

Login:

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass@123"
}
```

Forgot password:

```http
POST /api/auth/forget-password/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

Reset password:

```http
POST /api/auth/reset-password/
Content-Type: application/json

{
  "token": "<reset-token>",
  "new_password": "newStrongPass123",
  "confirm_password": "newStrongPass123"
}
```

## Organization APIs

All organization endpoints require a JWT access token:

```http
Authorization: Bearer <access-token>
```

List organizations:

```http
GET /api/organizations/
```

Create organization:

```http
POST /api/organizations/
Content-Type: application/json

{
  "name": "My Company",
  "description": "Team workspace"
}
```

Get organization:

```http
GET /api/organizations/<organization-id>/
```

Update organization:

```http
PUT /api/organizations/<organization-id>/
Content-Type: application/json

{
  "name": "Updated Company",
  "description": "Updated description"
}
```

Delete organization:

```http
DELETE /api/organizations/<organization-id>/
```

Invite user to organization:

```http
POST /api/organizations/<organization-id>/invite/
Content-Type: application/json

{
  "email": "member@example.com",
  "role": "member"
}
```

## Invitation APIs

List current user's pending invitations:

```http
GET /api/organizations/invitations/
Authorization: Bearer <access-token>
```

Accept invitation:

```http
POST /api/organizations/invitations/<invitation-id>/accept/
Authorization: Bearer <access-token>
```

Decline invitation:

```http
POST /api/organizations/invitations/<invitation-id>/decline/
Authorization: Bearer <access-token>
```

Note: the accept and decline APIs use the invitation ID, not the organization ID.

## Celery

If `CELERY_BROKER_URL` or `REDIS_URL` is configured, Celery uses that broker. If no broker URL is configured, tasks run eagerly in the Django process for local development.

Optional environment variables:

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

Run a worker when using Redis:

```bash
celery -A teamhub worker -l info
```

Run Celery Beat for scheduled cleanup tasks:

```bash
celery -A teamhub beat -l info
```

## Useful Commands

Run migrations:

```bash
python manage.py migrate
```

Make migrations:

```bash
python manage.py makemigrations
```

Run server:

```bash
python manage.py runserver
```

Open Django shell:

```bash
python manage.py shell
```

## Notes

- Email is currently configured to use Django's console email backend, so verification and reset links print in the terminal during local development.
- JWT access tokens expire after 15 minutes.
- JWT refresh tokens expire after 7 days.
- SQLite is used by default for local development.
