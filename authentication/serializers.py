from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from accounts.email import send_verification_email, send_forgetpassword_email
from django.contrib.auth import authenticate
from accounts.utils import verify_forget_password_token

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    """validate_password : 
            it means for serializer field validation 
            write validate_ and the field anme on serializer.save() it will check method for that field and will run code inside it """

    def validate_password(self, value):
        validate_password(value)

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "password do not match"})
        return attrs

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("email already exists ")
        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["email"],
            password=validated_data["password"],
            email=validated_data["email"].lower(),
            email_verified=False,
        )

        send_verification_email.delay(user.id)

        return user


class LoginSerializer(serializers.Serializer):
    """
    1. Get user by email
    2. Check password
    3. Check email_verified
    4. Return user in attrs
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = authenticate(username=email, password=password)

        if not user:

            raise serializers.ValidationError("username or password is invalid")

        attrs["user"] = user

        return attrs


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("please enter a valid email adress")

        send_forgetpassword_email.delay(user.id)

        return attrs


class ResetPasswordSerializer(serializers.Serializer):

    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "password does not match"}
            )
        token = data["token"]
        user_id = verify_forget_password_token(token)

        if not user_id:
            raise serializers.ValidationError({"token": "invalid_token"})
        user = User.objects.filter(id=user_id).first()

        if not user:
            raise serializers.ValidationError({"token": "user doesn"})
        data["user"] = user

        return data
