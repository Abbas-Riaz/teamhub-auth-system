from django.contrib.auth import get_user_model
from accounts.utils import verify_email_token  # your signing-based verify function

User = get_user_model()


def verify_email_token_service(token: str):
    """
    Verifies email token.
    Returns:
        - "VERIFIED" → user just verified
        - "ALREADY_VERIFIED" → user already verified
        - "INVALID" → token invalid/expired/user missing
    """
    user_id = verify_email_token(token)

    if not user_id:
        return "INVALID"

    user = User.objects.filter(id=user_id).first()
    if not user:
        return "INVALID"

    if user.email_verified:
        return "ALREADY_VERIFIED"

    user.email_verified = True
    user.save(update_fields=["email_verified"])
    return "VERIFIED"
