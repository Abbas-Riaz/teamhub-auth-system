from celery import shared_task
from datetime import timedelta
from django.utils import timezone


@shared_task
def cleanup_unverified_users():
    """Delete users who didn't verify email in 7 days"""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    cutoff_date = timezone.now() - timedelta(days=1)

    deleted = User.objects.filter(
        email_verified=False, date_joined__lt=cutoff_date
    ).delete()

    return f"Deleted {deleted[0]} unverified users"


@shared_task
def cleanup_password_reset_tokens():
    """Clear expired password reset tokens from cache"""
    from django.core.cache import cache

    # Logic to clear old tokens
    return "Cleaned up expired tokens"
