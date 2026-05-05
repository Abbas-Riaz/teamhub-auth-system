from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailVerifiedBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        user = User.objects.filter(
            Q(email__iexact=username) | Q(username__iexact=username)
        ).first()
        if not user:
            return None

        if not user.check_password(password):
            return None

        if not self.user_can_authenticate(user):
            return None

        if user.is_superuser:
            return user

        if not user.email_verified:
            return None

        return user
