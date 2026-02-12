from django.shortcuts import render
from rest_framework.views import APIView
from authentication.serializers import RegisterSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer

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

        serializer_data = RegisterSerializer(data=request.data)

        if serializer_data.is_valid():
            serializer_data.save()
            return Response(
                {"message": "verification email is being sent"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)
