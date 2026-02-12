from django.core import signing
from django.core.signing import BadSignature, SignatureExpired

TOKEN_SALT = (
    "email-verification"
    """like different salt for differnet token so django can distiguish between them its a password reset or registeration linke if one get expired or leak other are safe """
)


def generate_email_token(user_id):

    return signing.dumps(
        user_id,
        salt=TOKEN_SALT,
    )


def verify_email_token(token, max_age=24 * 60 * 60):
    """PARAMETER :
    Token : token from user to that it will click
    max_age = token expiry time like in seconds 24 hours
    token has encode timestamp when it was created check token expiry date etc and return user_id
    """
    try:
        user_id = signing.loads(token, salt=TOKEN_SALT, max_age=max_age)
        return user_id
    except (BadSignature, SignatureExpired):
        return None
