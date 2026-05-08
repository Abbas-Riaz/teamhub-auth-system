from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Invitation


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=60,
)
def send_invitation_email(self, invitation_id):
    """
    Send invitation email to user

    Args:
        invitation_id: UUID of invitation
    """
    try:
        invitation = Invitation.objects.select_related(
            "organization", "invited_by"
        ).get(id=invitation_id)

    except Invitation.DoesNotExist:
        # Invitation deleted before email sent
        return "Invitation not found"

    # Build invitation link
    # In production: https://yourapp.com/accept-invite?token=...
    accept_link = f"http://localhost:3000/accept-invite?token={invitation.token}"

    # Email content
    subject = f"You're invited to join {invitation.organization.name}"

    message = f"""
Hello,

{invitation.invited_by.email} has invited you to join {invitation.organization.name} as {invitation.role}.

Click the link below to accept the invitation:
{accept_link}

This invitation will expire on {invitation.expires_at.strftime('%B %d, %Y at %I:%M %p')}.

If you don't have an account, you'll be able to create one when you accept the invitation.

Thanks,
{invitation.organization.name} Team
    """

    # Send email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
        fail_silently=False,
    )

    return f"Invitation email sent to {invitation.email}"
