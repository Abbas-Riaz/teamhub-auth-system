from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailVerifiedBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        if not user.email_verified:
            return None

        return user
