from django.db import models

"""import django abstract user to make custom model for user"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, null=True, blank=True)
    """user move to multiple orgs in saas system track it where it was login last time so it does not need to select org every time """
    last_org_id = models.IntegerField(blank=True, null=True)
