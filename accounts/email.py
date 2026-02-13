from django.core.mail import send_mail
from django.conf import settings
from .utils import generate_email_token, generate_forget_password_token


def send_verification_email(user):
    token = generate_email_token(user.id)

    verify_url = f"http://localhost:8000/api/auth/verify-email/?token={token}"

    send_mail(
        subject="Verify your email",
        message=f"Click the link to verify your account:\n{verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_forgetpassword_email(user):
    token = generate_forget_password_token(user.id)

    verify_url = f"http://localhost:8000/api/auth/reset-password/?token={token}"
    send_mail(
        subject="reset password ",
        message=f"Click the link to reset your password:\n{verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
