# TeamHub Auth System Documentation

## Overview

TeamHub Auth System is a Django REST Framework backend for managing users, authentication, organizations, memberships, and invitations.

The project is designed for a SaaS-style team workspace where a user can own or join multiple organizations. Organizations have role-based memberships, and owners/admins can invite other users by email.

## Main Applications

### `accounts`

The `accounts` app contains the custom user model and account-related background cleanup tasks.

Main model:

- `User`

Important fields:

- `email`: unique email address used for authentication
- `email_verified`: tracks whether the user has verified their email
- `totp_secret`: reserved for two-factor authentication support
- `last_org_id`: stores the user's last selected organization

The project uses:

```python
AUTH_USER_MODEL = "accounts.User"
```

### `authentication`

The `authentication` app handles public auth flows.

Responsibilities:

- User registration
- Email verification
- Login
- Forgot password
- Reset password

Routes:

```text
POST /api/auth/register/
POST /api/auth/login/
GET  /api/auth/verify-email/?token=<token>
POST /api/auth/forget-password/
POST /api/auth/reset-password/
```

Authentication uses JWT through `djangorestframework-simplejwt`.

Token lifetimes:

- Access token: 15 minutes
- Refresh token: 7 days

### `organizations`

The `organizations` app handles organizations, memberships, roles, and invitations.

Main models:

- `Organization`
- `OrganizationMembership`
- `Invitation`

## Data Model

### Organization

Represents a company, team, or workspace.

Important fields:

- `id`: UUID primary key
- `name`: organization name
- `slug`: unique slug generated from the name
- `description`: optional text description
- `owner`: user who owns the organization
- `members`: many-to-many relationship with users through `OrganizationMembership`

### OrganizationMembership

Connects users to organizations and stores their role.

Available roles:

- `owner`
- `admin`
- `member`
- `viewer`

Each user can only have one membership per organization.

### Invitation

Represents an invitation sent to an email address.

Important fields:

- `organization`: organization the user is invited to join
- `email`: invited email address
- `role`: role assigned after accepting
- `invited_by`: user who sent the invitation
- `status`: invitation state
- `token`: unique invitation token
- `expires_at`: invitation expiry date/time

Available statuses:

- `pending`
- `accepted`
- `declined`
- `expired`

## API Authentication

Protected endpoints require a JWT access token:

```http
Authorization: Bearer <access-token>
```

If the token is missing, expired, or invalid, the API returns an authentication error.

## API Reference

### Register User

```http
POST /api/auth/register/
Content-Type: application/json
```

Body:

```json
{
  "email": "user@example.com",
  "password": "StrongPass@123",
  "password2": "StrongPass@123"
}
```

Result:

- Creates a new user
- Sends or prints an email verification link
- User must verify email before login, depending on backend rules

### Verify Email

```http
GET /api/auth/verify-email/?token=<token>
```

Result:

- Marks the user's email as verified

### Login

```http
POST /api/auth/login/
Content-Type: application/json
```

Body:

```json
{
  "email": "user@example.com",
  "password": "StrongPass@123"
}
```

Result:

- Returns JWT access and refresh tokens

### Forgot Password

```http
POST /api/auth/forget-password/
Content-Type: application/json
```

Body:

```json
{
  "email": "user@example.com"
}
```

Result:

- Sends or prints a password reset token/link

### Reset Password

```http
POST /api/auth/reset-password/
Content-Type: application/json
```

Body:

```json
{
  "token": "<reset-token>",
  "new_password": "newStrongPass123",
  "confirm_password": "newStrongPass123"
}
```

Result:

- Updates the user's password if the token is valid

## Organization Flow

### Create Organization

```http
POST /api/organizations/
Authorization: Bearer <access-token>
Content-Type: application/json
```

Body:

```json
{
  "name": "My Company",
  "description": "Team workspace"
}
```

Result:

- Creates the organization
- Makes the authenticated user the owner
- Creates an `OrganizationMembership` with role `owner`

### List Organizations

```http
GET /api/organizations/
Authorization: Bearer <access-token>
```

Result:

- Returns organizations where the authenticated user is a member

### Get Organization Detail

```http
GET /api/organizations/<organization-id>/
Authorization: Bearer <access-token>
```

Result:

- Returns organization detail only if the user is a member

### Update Organization

```http
PUT /api/organizations/<organization-id>/
Authorization: Bearer <access-token>
Content-Type: application/json
```

Body:

```json
{
  "name": "Updated Company",
  "description": "Updated description"
}
```

Result:

- Updates organization data
- Only the owner can update

### Delete Organization

```http
DELETE /api/organizations/<organization-id>/
Authorization: Bearer <access-token>
```

Result:

- Deletes the organization
- Only the owner can delete

## Invitation Flow

### Send Invitation

```http
POST /api/organizations/<organization-id>/invite/
Authorization: Bearer <access-token>
Content-Type: application/json
```

Body:

```json
{
  "email": "member@example.com",
  "role": "member"
}
```

Result:

- Creates a pending invitation
- Sends the invitation email using Celery if a broker is configured
- Runs synchronously in local eager mode if no broker is configured

Only owners and admins can invite users.

### List Pending Invitations

```http
GET /api/organizations/invitations/
Authorization: Bearer <access-token>
```

Result:

- Returns pending invitations where `invitation.email` matches the authenticated user's email

### Accept Invitation

```http
POST /api/organizations/invitations/<invitation-id>/accept/
Authorization: Bearer <access-token>
```

Result:

- Validates the invitation
- Creates an organization membership for the authenticated user
- Updates invitation status to `accepted`

Important: this route uses the invitation ID, not the organization ID.

### Decline Invitation

```http
POST /api/organizations/invitations/<invitation-id>/decline/
Authorization: Bearer <access-token>
```

Result:

- Updates invitation status to `declined`

## Permissions

Current permission behavior:

- Auth endpoints are public unless the view requires otherwise
- Organization list/detail require authentication
- Organization detail is only visible to members
- Organization update/delete are owner-only
- Invitations can be sent by owners and admins
- Invitations can only be accepted by the user whose email matches the invitation

## Background Tasks

Celery is used for asynchronous and scheduled work.

Configured scheduled tasks:

```text
cleanup-unverified-users
cleanup-tokens
```

If no Redis/Celery broker is configured, tasks run eagerly inside the Django process:

```python
CELERY_TASK_ALWAYS_EAGER = True
```

## Cache and Redis

If `REDIS_URL` is configured, the project uses Redis cache through `django-redis`.

If `REDIS_URL` is not configured, the project falls back to Django local memory cache.

This makes local development easier because Redis is optional.

## Email Behavior

The current settings use Django's console email backend:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

During development, verification and reset emails are printed in the terminal instead of being sent to a real inbox.

## Environment Variables

Required:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Optional:

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Local Development Workflow

Install dependencies:

```bash
pip install -r requirements.txt
pip install python-decouple dj-database-url whitenoise
```

Run migrations:

```bash
python manage.py migrate
```

Start the API server:

```bash
python manage.py runserver
```

Use `api.http` to test requests from VS Code or another HTTP client.

## Common Issues

### Invitation accept route returns 404

Use:

```http
POST /api/organizations/invitations/<invitation-id>/accept/
```

Do not use:

```http
POST /api/organizations/<organization-id>/accept/
```

The accept endpoint expects an invitation ID.

### Verification or reset email is not in inbox

In local development, emails are printed in the terminal because the console email backend is enabled.

### Celery worker is not running

If no broker is configured, Celery tasks run eagerly. If Redis is configured, start a worker:

```bash
celery -A teamhub worker -l info
```

## Deployment Notes

Before deploying:

- Set `DEBUG=False`
- Configure `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Configure a production database
- Configure a real email backend
- Configure Redis/Celery if background tasks should run asynchronously
- Run migrations
- Collect static files if static files are served by Django/Whitenoise

Recommended production commands:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```
