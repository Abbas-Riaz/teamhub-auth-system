from django.shortcuts import render
from rest_framework.views import APIView
from authentication.serializers import (
    RegisterSerializer,
    LoginSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    RegisterSerializer,
)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

"""import user model to make its verification successfull after verifying token"""

from django.contrib.auth import get_user_model

""" email verification servicd import from services folder """
from accounts.services.email_verification import verify_email_token_service

User = get_user_model()

"""
veiw for registering user :

        user will enter data 
        date is validated 
        on sucessfull user creation response is sent 
        
"""

"""function for verifying token """


from accounts.utils import verify_email_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.services.email_verification import verify_email_token_service


class VerifyEmailView(APIView):
    permission_classes = []
    authentication_classes = []

    """first we will extract the token from query 
       then pass this token to email verification service where it checks the token validity
       and return an appropriate response to user after clicking on link sent in email  """

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"error": "Invalid or expired verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = verify_email_token_service(token)

        if result == "VERIFIED":
            return Response(
                {"message": "Email verified successfully"}, status=status.HTTP_200_OK
            )
        elif result == "ALREADY_VERIFIED":
            return Response(
                {"message": "Email already verified"}, status=status.HTTP_200_OK
            )
        else:  # INVALID
            return Response(
                {"error": "Invalid or expired verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterView(APIView):

    def post(self, request):
        """
        used to register a new user
        and when data is validate sucessfully
        promt user to check email for verifcation so we can avoid fake email registrations

        """

        serializer_data = RegisterSerializer(data=request.data)

        if serializer_data.is_valid():
            serializer_data.save()
            return Response(
                {"message": "verification email is being sent"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]
            email = user.email
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "email": email,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(APIView):

    permission_classes = []
    authentication_classes = []
    """
    this view recieve a post request that contain email of user when it click forget password and enter emails

    then we share a link through email to reset password

    """

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                {"message": "verification email is being sent"},
                status=status.HTTP_201_CREATED,
            )


class ResetPasswordView(APIView):
    """
    Docstring for ResetPasswordVie
        accepts the user token along with reset pass
        verify the token validity and change the password in db
        consider edge cases :
             if token is not valid or expired
             password should not match old pass
             validate pass and store in hash
    """

    def post(self, request):

        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            new_password = serializer.validated_data["new_password"]

            user.set_password(new_password)
            user.save()

            return Response(
                {
                    "message": "Password has been reset successfully. You can now login with your new password."
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
