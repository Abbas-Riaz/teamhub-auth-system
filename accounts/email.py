from django.core.mail import send_mail
from django.conf import settings
from .utils import generate_email_token, generate_forget_password_token
from django.contrib.auth import get_user_model

User = get_user_model()
"""for using celery import shared task"""
from celery import shared_task
from smtplib import SMTPException


@shared_task(
    bind=True,
    autoretry_for=(SMTPException, ConnectionError, TimeoutError),
    retry_kwargs={"max_retries": 3},
    retry_backoff=60,
)
def send_verification_email(self, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return
    token = generate_email_token(user.id)

    verify_url = f"http://localhost:8000/api/auth/verify-email/?token={token}"

    send_mail(
        subject="Verify your email",
        message=f"Click the link to verify your account:\n{verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@shared_task(
    bind=True,
    autoretry_for=(SMTPException, ConnectionError, TimeoutError),
    retry_kwargs={"max_retries": 3},
    retry_backoff=60,
)
def send_forgetpassword_email(self, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return
    token = generate_forget_password_token(user.id)

    verify_url = f"http://localhost:8000/api/auth/reset-password/?token={token}"
    send_mail(
        subject="reset password ",
        message=f"Click the link to reset your password:\n{verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
