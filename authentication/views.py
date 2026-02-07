from django.shortcuts import render
from rest_framework.views import APIView
from authentication.serializers import RegisterSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer

"""import user model to make its verification successfull after verifying token"""

from django.contrib.auth import get_user_model

User = get_user_model()

"""
veiw for registering user :

        user will enter data 
        date is validated 
        on sucessfull user creation response is sent 
        
"""

"""function for verifying token """

from accounts.utils import verify_email_token


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


class VerifyEmailView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = verify_email_token(token)

        if not user_id:
            return Response(
                {"error": "user does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = User.objects.filter(id=user_id).first()

        user.email_verified = True

        user.save(update_fields=["email_verified"])

        return Response(
            {"message": "user verified sucessfully"}, status=status.HTTP_200_OK
        )
