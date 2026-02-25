from django.urls import path
from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    ForgetPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("verify-email/", VerifyEmailView.as_view()),
    path("forget-password/", ForgetPasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
