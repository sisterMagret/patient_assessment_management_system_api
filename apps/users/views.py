import logging
from datetime import datetime, timedelta

import pytz
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import (
    Address,
    Allergy,
    AuthToken,
    EmergencyContact,
    Medication,
    Patient,
    Practitioner,
    PractitionerSpecialization,
    User,
)
from apps.users.serializer import (
    AddressSerializer,
    AllergySerializer,
    EmergencyContactSerializer,
    PractitionerDocumentUploadSerializer,
    MedicationSerializer,
    OauthCodeSerializer,
    PatientFormSerializer,
    PatientRegistrationSerializer,
    PatientSerializer,
    PractitionerFormSerializer,
    PractitionerRegistrationSerializer,
    PractitionerSerializer,
    PractitionerSpecializationSerializer,
    UserFormSerializer,
    UserSerializer,
)
from apps.utils.base import (
    Addon,
    BaseModelViewSet,
    BaseNoAuthViewSet,
    BaseViewSet,
)
from apps.utils.encrypt_util import Encrypt
from apps.utils.enums import UserGroup, UserType
from apps.utils.permissions import (
    patient_access_only,
    practitioner_access_only,
)
from apps.utils.validators import validate_file

logger = logging.getLogger("user")


class AuthViewSet(ViewSet, Addon):
    """
    Authentication and user-related operations.
    """

    serializer_class = UserSerializer

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    def get_user(username):
        """
        Retrieve user by email, username, or phone number.
        :param username: str
        :return: User instance or None
        """
        return User.objects.filter(
            Q(email=username)
            | Q(username=username)
            | Q(phone_number=username)
        ).first()

    @staticmethod
    def get_data(request) -> dict:
        """
        Extract data from the request.
        :param request: Request object
        :return: dict
        """
        return (
            request.data
            if isinstance(request.data, dict)
            else request.data.dict()
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Can be phone number, email, or username.",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User password"
                ),
            },
        ),
        operation_summary="LOGIN ENDPOINT FOR ALL USERS",
    )
    @action(
        detail=False, methods=["post"], description="Login authentication"
    )
    def login(self, request, *args, **kwargs):
        """
        User login authentication and token generation.
        :param request: HTTP request
        :return: Response
        """
        data = self.get_data(request)

        username, password = data.get("username"), data.get("password")
        required_fields = ["username", "password"]

        for field in required_fields:
            if field not in data:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": f"{field} missing from the request",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid credentials. Please provide valid credentials.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.last_login = make_aware(
            datetime.now(), timezone=pytz.timezone("Africa/Lagos")
        )
        user.save(update_fields=["last_login"])

        message = f"You signed in from {self.get_device(request).get('device')} device with ip address {self.get_ip_address(request)}"

        user.email_user(
            subject="login notification",
            message=message,
            from_email="info@mail.com",
        )

        return Response(
            {
                "status": status.HTTP_200_OK,
                "data": UserSerializer(user).data,
                "token": self.get_tokens_for_user(user),
                "oauth": self.get_oauth(user),
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def error_message_formatter(serializer_errors):
        """
        Formats serializer error messages into a dictionary.
        :param serializer_errors: dict
        :return: dict
        """
        return {
            field: message[0]
            for field, message in serializer_errors.items()
        }

    @staticmethod
    def get_oauth(user):
        """
        Generate OAuth token for the user.
        :param user: User instance
        :return: dict containing the OAuth token
        """
        expire = datetime.now() + timedelta(hours=2)
        payload = Encrypt().jwt_encrypt(
            {
                "username": user.username,
                "expire": expire.strftime("%Y-%m-%d %H:%M"),
            }
        )
        return {"auth_code": payload}

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="OAuth code retrieved from the server",
                ),
            },
        ),
        operation_summary="Exchange the OAuth code to obtain credentials",
    )
    @action(
        detail=False,
        methods=["post"],
        description="Obtain access tokens using OAuth code",
        url_path="oauth",
    )
    def obtain_oauth(self, request):
        """
        Exchange OAuth code for JWT tokens.
        :param request: HTTP request
        :return: Response
        """
        data = self.get_data(request)
        serializer = OauthCodeSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                {
                    "errors": self.error_message_formatter(
                        serializer.errors
                    ),
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = Encrypt().jwt_decrypt(serializer.validated_data["code"])

        if not all([payload.get("username"), payload.get("expire")]):
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid authorization code",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        expire = make_aware(
            datetime.strptime(payload["expire"], "%Y-%m-%d %H:%M"),
            timezone=pytz.timezone("Africa/Lagos"),
        )

        if (
            make_aware(
                datetime.now(), timezone=pytz.timezone("Africa/Lagos")
            )
            > expire
        ):
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Authorization code expired",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username=payload["username"]).first()

        if not user:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid authorization code",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "tokens": self.get_tokens_for_user(user),
                "data": UserSerializer(user).data,
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        request_body=PatientRegistrationSerializer,
        operation_description=f"This endpoint handles user onboarding based on account_type {UserGroup.to_list()}",
        responses={},
        operation_summary="USER ONBOARD ENDPOINT",
    )
    @action(
        detail=False,
        methods=["post"],
        description="on boarding authentication",
        url_path=r"register/(?P<account_type>[^/]+)",
    )
    def register(self, request, account_type):
        context = {"status": status.HTTP_200_OK}

        if account_type not in [UserGroup.PRACTITIONER, UserGroup.USER]:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Kindly supply a valid account type {UserGroup.to_list()}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_data(request)
        if account_type == UserGroup.PRACTITIONER:
            return self.create_practitioner_account(data, request)
        else:
            serializer_dict = {
                UserGroup.USER: PatientRegistrationSerializer,
            }
            return self.generic_create_user(
                data, serializer_dict[account_type], request
            )

    def create_practitioner_account(self, data, request):
        serializer = PractitionerRegistrationSerializer(data=data)

        if serializer.is_valid():
            if User.objects.filter(
                phone_number=data.get("phone_number")
            ).exists():
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "User with this phone number already exists",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = serializer.save()
            token = self.unique_number_generator(AuthToken, "token", 4)
            self.create_auth_token(
                {
                    "type": 2,
                    "token": token,
                    "status": 0,
                    "user": user,
                    "expiry": make_aware(datetime.now(), timezone=pytz.utc)
                    + timedelta(days=3),
                }
            )

            message = (
                f"account created and your verification token is {token}"
            )

            user.email_user(
                subject="Account created",
                message=message,
                from_email="info@mail.com",
            )
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Account created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "errors": self.error_message_formatter(serializer.errors),
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def generic_create_user(self, data, serializer, request):
        serializer = serializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            token = self.unique_number_generator(AuthToken, "token", 4)
            self.create_auth_token(
                {
                    "type": 2,
                    "token": token,
                    "status": 0,
                    "user": user,
                    "expiry": make_aware(datetime.now(), timezone=pytz.utc)
                    + timedelta(days=3),
                }
            )

            message = (
                f"account created and your verification token is {token}"
            )

            user.email_user(
                subject="Account created",
                message=message,
                from_email="info@mail.com",
            )
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Account created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "errors": self.error_message_formatter(serializer.errors),
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="This is the user email",
                ),
            },
        ),
        operation_description="This endpoint handles user request for password reset",
        responses={},
        operation_summary="FORGET ENDPOINT",
    )
    @action(
        detail=False,
        methods=["post"],
        description="Forgot password endpoint",
        url_path="password/forget",
    )
    def forget_password(self, request, *args, **kwargs):
        data = self.get_data(request)
        username = data.get("username")

        if not username:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Kindly supply a valid parameter",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=username).first()

        if not user:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Supplied credential not associated to any user",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        AuthToken.objects.filter(user=user, type=0).delete()
        token = self.unique_number_generator(AuthToken, "token", 4)

        AuthToken.objects.create(user=user, token=token, type=0)

        message = f"Password reset token is {token}"
        user.email_user(
            subject="Password Reset",
            message=message,
            from_email="info@mail.com",
        )

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Token generated successfully",
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "token": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Token generated to reset password",
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New password for the user",
                ),
            },
        ),
        operation_description="This endpoint handles user request to reset password",
        responses={},
        operation_summary="RESET PASSWORD ENDPOINT",
    )
    @action(
        detail=False,
        methods=["post"],
        description="Reset password endpoint",
        url_path="password/reset",
    )
    def reset_password(self, request, *args, **kwargs):
        data = self.get_data(request)
        token = data.get("token")
        new_password = data.get("new_password")

        if not token or not new_password:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Token and new password are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        auth_token = AuthToken.objects.filter(token=token, type=0).first()

        if not auth_token:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = auth_token.user
        user.set_password(new_password)
        user.save()

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Password updated successfully",
            },
            status=status.HTTP_200_OK,
        )

    def verify_user(self, request, token):
        context = {"status": status.HTTP_200_OK}
        try:

            if not AuthToken.objects.filter(
                token=token, status=0, type=2
            ).exists():
                raise Exception(
                    "System could not validate your credentials ,Kindly ensure you enter correct code sent to your mail"
                )
            instance = AuthToken.objects.filter(
                token=token, status=0, type=2
            ).first()
            if instance.user.is_verified:
                raise Exception("User already verified")
            instance.user.is_verified = True
            instance.user.save()
            message = f"Your account have been activated"
            instance.user.email_user(
                subject="Account activation",
                message=message,
                from_email="info@mail.com",
            )
            context.update(
                {
                    "message": "ok",
                    "data": self.serializer_class(instance.user).data,
                    "status": status.HTTP_200_OK,
                }
            )
            self.delete_auth_token({"token": token})
        except Exception as ex:
            context.update(
                {
                    "message": "BAD_REQUEST",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "errors": str(ex),
                }
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "action": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="action can be either be verification, password_reset",
                )
            },
        ),
        operation_description="This endpoint verifies the user with their provided token",
        responses={},
        operation_summary="VERIFY TOKEN ENDPOINT",
    )
    @action(
        detail=False,
        methods=["post"],
        description="Verify token endpoint",
        url_path=r"verify-token/(?P<token>[^/]+)",
    )
    def verify_token(self, request, token):
        """
        Verify a user's token.
        :param request: HTTP request
        :return: Response
        """
        context = {"status": status.HTTP_200_OK}
        try:
            if token is None:
                raise Exception("Kindly supply a valid token")

            data = self.get_data(request)

            if data.get("action") not in [
                "verification",
                "password_reset",
            ]:
                raise Exception(
                    "Kindly supply an action [verification, password_reset]"
                )
            if data.get("action") == "verification":
                if not AuthToken.objects.filter(
                    token=token, status=0, type=2
                ).exists():
                    raise Exception(
                        "System could not validate your credentials ,"
                        "Kindly ensure you copy correctly, the code sent to your phone"
                    )
                return self.verify_user(request=request, token=token)
            elif data.get("action") == "password_reset":
                if not AuthToken.objects.filter(
                    token=token, status=0, type=0
                ).exists():
                    raise Exception(
                        "System could not validate your credentials ,"
                        "Kindly ensure your click the link sent to your mail"
                    )
                return self.password_reset(request, token)

        except Exception as ex:
            context.update(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": str(ex),
                    "error": str(ex),
                }
            )
        return Response(context, status=context["status"])

    def password_reset(self, request, token):
        context = {"status": status.HTTP_200_OK}
        try:
            auth_user = AuthToken.objects.get(token=token)
            context.update(
                {
                    "message": "OK",
                    "status": status.HTTP_200_OK,
                    "data": UserSerializer(auth_user.user).data,
                }
            )
            self.delete_auth_token({"token": token})
        except Exception as ex:
            context.update(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "BAD_REQUEST",
                    "error": str(ex),
                }
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "action": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="action can be either be email_verification, password_reset,invite_verification",
                )
            },
        ),
        operation_description="Resend Verification Token",
        responses={},
        operation_summary="Resend  Token",
    )
    @action(
        detail=False,
        methods=["post"],
        description="resend token endpoint",
        url_path=r"resend-token/(?P<email>[^/]+)",
    )
    def resend_token(self, request, email):
        context = {
            "status": status.HTTP_200_OK,
            "message": "Token sent successfully",
        }

        try:
            data = self.get_data(request)
            if not User.objects.filter(email=email).exists():
                raise ValidationError(
                    "User with this mobile does not exist inside our system"
                )

            if data.get("action") not in [
                "verification",
                "password_reset",
            ]:
                raise Exception(
                    "Kindly supply an action [verification, password_reset]"
                )
            user = User.objects.filter(email=email).first()
            if data.get("action") == "verification":
                number_token = self.unique_number_generator(
                    AuthToken, "token", 4
                )

                self.delete_auth_token({"user": user, "type": 2})
                auth_token = self.create_auth_token(
                    {
                        "type": 2,
                        "token": number_token,
                        "status": 0,
                        "user": user,
                        "expiry": make_aware(
                            datetime.now(), timezone=pytz.utc
                        )
                        + timedelta(minutes=20),
                    }
                )
            elif data.get("action") == "password_reset":
                number_token = self.unique_number_generator(
                    AuthToken, "token", 4
                )

                self.delete_auth_token({"user": user, "type": 0})
                auth_token = self.create_auth_token(
                    {
                        "type": 0,
                        "token": number_token,
                        "status": 0,
                        "user": user,
                        "expiry": make_aware(
                            datetime.now(), timezone=pytz.utc
                        )
                        + timedelta(minutes=20),
                    }
                )

            message = f"Your token {number_token}"
            resp = user.email_user(
                subject="New Token",
                message=message,
                from_email="info@mail.com",
            )
            if resp is None:
                context.update(
                    {
                        "status": status.HTTP_200_OK,
                        "message": f"New token sent successfully",
                    }
                )
            else:
                auth_token.delete()
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Token could not be sent currently ,Kindly try again",
                    }
                )
        except ValidationError as ex:
            context.update(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": ex.messages[0],
                }
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Logout",
        responses={},
        operation_summary="logout",
    )
    @action(
        detail=False,
        methods=["get"],
        description="resend token endpoint",
        url_path=r"logout",
    )
    def account_logout(self, request):
        try:
            logout(request)
        except Exception as ex:
            pass
        return redirect("/")


class UserViewSet(BaseViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return self.queryset.exclude(
            user_role__in=[UserType.ADMIN, UserType.PRACTITIONER]
        )

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs.get("pk"))

    @swagger_auto_schema(
        operation_summary="List all users account",
        operation_description="Retrieve a paginated list of users.",
        responses={
            200: openapi.Response(
                "Success", PractitionerSerializer(many=True)
            )
        },
    )
    def list(self, request, *args, **kwargs):
        context = {}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_queryset(),
                serializer_class=self.serializer_class,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="Retrieve user information",
    )
    @action(
        detail=False,
        methods=["get"],
        description="Get user profile information",
    )
    def me(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update(
                {"data": self.serializer_class(request.user).data}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=UserFormSerializer,
        operation_description="",
        responses={},
        operation_summary="Update user profile endpoint",
    )
    def update(self, request, *args, **kwargs):
        context = {"status": status.HTTP_400_BAD_REQUEST}
        try:
            instance = request.user
            data = self.get_data(request)
            serializer = UserFormSerializer(data=data, instance=instance)
            if serializer.is_valid():

                all_users_exclude_current = User.objects.all().exclude(
                    id=request.user.id
                )

                if (
                    serializer.validated_data.get("phone_number")
                    and all_users_exclude_current.filter(
                        phone_number=serializer.validated_data.get(
                            "phone_number"
                        )
                    ).exists()
                ):
                    raise Exception("Phone number already being used")

                if serializer.validated_data.get("email"):
                    if all_users_exclude_current.filter(
                        email=serializer.validated_data.get("email")
                    ).exists():
                        raise Exception("Email already being used")
                obj = serializer.update(
                    instance=instance,
                    validated_data=serializer.validated_data,
                )
                context.update(
                    {
                        "data": self.serializer_class(obj).data,
                        "status": status.HTTP_200_OK,
                    }
                )
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(
                            serializer.errors
                        )
                    }
                )
        except Exception as ex:
            context.update({"message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="Upload user profile picture",
    )
    @action(
        detail=True,
        methods=["put"],
        description="Upload Profile picture",
        url_path="upload",
    )
    def upload(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:

            if request.FILES.get("avatar") is not None:
                file = request.FILES["avatar"]
                validate_file(file)

                instance = request.user
                instance.avatar = file
                instance.save(update_fields=["avatar"])
                context.update(
                    {
                        "message": "Profile picture upload successfully",
                        "data": UserSerializer(
                            get_object_or_404(User, id=request.user.id)
                        ).data,
                    }
                )
            else:
                raise Exception("Kindly upload a valid image")
        except Exception as ex:
            context.update(
                {"message": str(ex), "status": status.HTTP_400_BAD_REQUEST}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "old_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="old password"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="new password"
                ),
            },
        ),
        operation_description="This endpoint handles new password reset",
        responses={},
        operation_summary="Update password  endpoint",
    )
    @action(
        detail=False,
        methods=["put"],
        description="Update password endpoint",
    )
    def update_password(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            user = request.user

            for key, value in data.items():
                if value == "" or value is None:
                    raise Exception(f"{key} is required")

            if user.check_password(data.get("old_password")) is True:
                user.set_password(data.get("new_password"))
                user.save()
                context.update(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "ok",
                        "data": self.serializer_class(user).data,
                    }
                )
            else:
                raise Exception(
                    "Password does not match with the old password, kindly try again"
                )
        except Exception as ex:
            context.update(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "BAD REQUEST",
                    "error": str(ex),
                }
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="The endpoint handles get user account"
    )
    def retrieve(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance = self.get_object()
            context.update({"data": self.serializer_class(instance).data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="The endpoint handles removing  user account"
    )
    def destroy(self, request, *args, **kwargs):
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            instance.delete()
            context.update({"message": "Account deleted successfully"})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])


class PractitionerViewSet(BaseViewSet):
    queryset = Practitioner.objects.select_related("user").all()
    serializer_class = PractitionerSerializer
    serializer_form_class = PractitionerFormSerializer

    def get_object(self):
        return get_object_or_404(Practitioner, pk=self.kwargs.get("pk"))

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(
        operation_summary="List all practitioner users account",
        operation_description="Retrieve a paginated list of practitioners associated with the authenticated user's organization.",
        responses={
            200: openapi.Response(
                "Success", PractitionerSerializer(many=True)
            )
        },
    )
    def list(self, request, *args, **kwargs):
        context = {}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_queryset(),
                serializer_class=self.serializer_class,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @action(
        detail=False,
        methods=["get"],
        description="Get practitioner profile settings (user preferred account)",
        url_path="settings",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def me(self, request, *args, **kwargs):
        context = {}
        try:
            practitioner = (
                self.get_queryset().filter(user=request.user).first()
            )
            if practitioner:
                context.update(
                    {
                        "status": status.HTTP_200_OK,
                        "data": self.serializer_class(practitioner).data,
                    }
                )
            else:
                context.update(
                    {
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Practitioner not found.",
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=PractitionerFormSerializer,
        operation_summary="Update practitioner settings",
        operation_description="Update the settings for a practitioner.",
        responses={
            200: openapi.Response("Success", PractitionerSerializer),
            400: openapi.Response("Validation Error"),
        },
    )
    def update(self, request, *args, **kwargs):
        context = {}
        try:
            instance = self.get_practitioner(request)

            if instance is None:
                raise Exception("Not authenticated")
            if instance.user.id != request.user.id:
                raise Exception("Can't perform this action")

            serializer = self.serializer_form_class(
                instance=instance, data=request.data
            )
            if serializer.is_valid():
                obj = serializer.update(
                    instance, serializer.validated_data
                )
                context.update(
                    {
                        "status": status.HTTP_200_OK,
                        "data": self.serializer_class(obj).data,
                    }
                )
            else:
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "errors": serializer.errors,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="Upload practitioner document",
        operation_description="Upload documents for the practitioner, such as certificates and identification.",
        request_body=PractitionerDocumentUploadSerializer,
        responses={
            200: openapi.Response("Success", PractitionerSerializer),
            400: openapi.Response("Validation Error"),
        },
    )
    @action(
        detail=True,
        methods=["put"],
        description="Upload practitioner documents",
        url_path="upload",
    )
    def upload(self, request, *args, **kwargs):
        context = {}
        try:
            instance = self.get_object()
            files_updated = False

            # Validate and save certificate
            if request.FILES.get("certificate"):
                instance.certificate = request.FILES["certificate"]
                files_updated = True

            # Validate and save means of identification
            if request.FILES.get(
                "means_of_identification"
            ) and request.data.get("means_of_identification_type"):
                instance.means_of_identification_type = request.POST.get(
                    "means_of_identification_type"
                )
                instance.means_of_identification = request.FILES[
                    "means_of_identification"
                ]
                files_updated = True

            if files_updated:
                instance.save()  # Save changes
                context.update(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "Documents uploaded successfully",
                        "data": self.serializer_class(instance).data,
                    }
                )
            else:
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "No files were uploaded.",
                    }
                )

        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=PractitionerSpecializationSerializer,
        operation_description="Add practitioner specialization",
        responses={},
        operation_summary="Practitioner specialization endpoint. You can't add more than 2",
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="specializations",
        serializer_class=PractitionerSpecializationSerializer,
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def specialization(self, request, *args, **kwargs):
        """
        This method handles adding practitioner specialization
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data_as_list(request)
            practitioner = self.get_practitioner(request)
            if request.user.id != practitioner.user.id:
                raise Exception("You can' perform this action")
            serializer = PractitionerSpecializationSerializer(
                data=data, many=True
            )
            if serializer.is_valid(raise_exception=True):
                specializations = {
                    PractitionerSpecialization.objects.get_or_create(**v)[
                        0
                    ].id
                    for v in data
                }
                print(specializations)
                practitioner.specializations.set(specializations)
                context.update({"data": "Specialization added"})
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="The endpoint handles get practitioner account"
    )
    def retrieve(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance = self.get_object()
            context.update({"data": self.serializer_class(instance).data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])


class PatientViewSet(BaseViewSet):
    queryset = Patient.objects.select_related("user").all()
    serializer_class = PatientSerializer
    serializer_form_class = PatientFormSerializer

    def get_object(self):
        return get_object_or_404(Patient, pk=self.kwargs.get("pk"))

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(
        operation_summary="List all patients users account",
        operation_description="Retrieve a paginated list of patients.",
        responses={
            200: openapi.Response("Success", PatientSerializer(many=True))
        },
    )
    def list(self, request, *args, **kwargs):
        context = {}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_queryset(),
                serializer_class=self.serializer_class,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @action(
        detail=False,
        methods=["get"],
        description="Get patient profile settings",
        url_path="settings",
    )
    def me(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance, _ = self.queryset.get_or_create(user=request.user)
            context.update({"data": self.serializer_class(instance).data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=PatientFormSerializer,
        operation_description="",
        responses={},
        operation_summary="Update patient settings",
    )
    @method_decorator(patient_access_only(), name="dispatch")
    def update(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            if request.user.id != self.get_patient(request).user.id:
                raise Exception("You can't update another user profile")
            data = self.get_data(request)
            instance, _ = self.queryset.get_or_create(user=request.user)
            serializer = self.serializer_form_class(
                instance=instance, data=data
            )
            if serializer.is_valid():
                obj = serializer.update(
                    instance=instance,
                    validated_data=serializer.validated_data,
                )
                context.update({"data": self.serializer_class(obj).data})
            else:
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                    }
                )
        except Exception as ex:
            context.update(
                {
                    "message": str(ex),
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="The endpoint handles get user account"
    )
    def retrieve(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance = self.get_object()
            context.update({"data": self.serializer_class(instance).data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="The endpoint handles removing  user account"
    )
    def destroy(self, request, *args, **kwargs):
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            instance.delete()
            context.update({"message": "Account deleted successfully"})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=EmergencyContactSerializer,
        operation_description="Add emergency contact",
        responses={},
        operation_summary="Patient emergency contact",
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="emergency-contact",
        serializer_class=EmergencyContactSerializer,
    )
    @method_decorator(patient_access_only(), name="dispatch")
    def emergency_contact(self, request, *args, **kwargs):
        """
        This method handles adding patient emergency contact
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)

            patient = self.get_patient(request)

            serializer = EmergencyContactSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                if patient.emergency_contact:
                    patient.emergency_contact.delete()

                emergency_contact = EmergencyContact.objects.create(**data)
                patient.emergency_contact = emergency_contact
                patient.save(update_fields=["emergency_contact"])
                context.update({"message": "Emergency contact added"})
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=AllergySerializer,
        operation_description="Add allergies",
        responses={},
        operation_summary="Patient allergies",
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="allergies",
        serializer_class=AllergySerializer,
    )
    @method_decorator(patient_access_only(), name="dispatch")
    def allergy(self, request, *args, **kwargs):
        """
        This method handles adding patient allergy
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data_as_list(request)
            patient = self.get_patient(request)
            serializer = AllergySerializer(data=data, many=True)
            if serializer.is_valid(raise_exception=True):

                allergies = [
                    Allergy.objects.get_or_create(**v)[0].id for v in data
                ]

                if patient.allergies.all():
                    allergies + list(
                        patient.allergies.all().values_list(
                            "id", flat=True
                        )
                    )

                patient.allergies.set(set(allergies))
                patient.save()
                context.update({"message": "Allergies added"})
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=MedicationSerializer,
        operation_description="Add medications",
        responses={},
        operation_summary="Patient medications",
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="medications",
        serializer_class=MedicationSerializer,
    )
    @method_decorator(patient_access_only(), name="dispatch")
    def medication(self, request, *args, **kwargs):
        """
        This method handles adding patient medication
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data_as_list(request)
            patient = self.get_patient(request)
            serializer = MedicationSerializer(data=data, many=True)
            if serializer.is_valid(raise_exception=True):
                medications = [
                    Medication.objects.get_or_create(**v)[0].id
                    for v in data
                ]
                if patient.medications.all():
                    medications + list(
                        patient.medications.all().values_list(
                            "id", flat=True
                        )
                    )
                patient.medications.set(set(medications))
                patient.save()
                context.update({"message": "Medication added"})
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])


class AddressViewSet(BaseModelViewSet):
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(
        operation_description="This endpoint handles listing addresses",
        operation_summary="User Delivery address endpoint",
    )
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_list(self.get_queryset()),
                serializer_class=self.serializer_class,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=AddressSerializer,
        operation_description="This endpoint handles adding address",
        operation_summary="Add address endpoint",
    )
    def create(self, request, *args, **kwargs):
        """
        This method handles adding delivery address
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                context.update(
                    {"data": self.serializer_class(instance).data}
                )
            else:
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=AddressSerializer,
        operation_description="This endpoint handles updating address",
        operation_summary="update address endpoint",
    )
    def update(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            instance = self.get_object()
            serializer = self.serializer_class(
                data=data, instance=instance
            )
            if serializer.is_valid():
                _ = serializer.update(
                    validated_data=serializer.validated_data,
                    instance=instance,
                )
                context.update(
                    {"data": self.serializer_class(self.get_object()).data}
                )
            else:
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="The endpoint handles get user account"
    )
    def retrieve(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance = self.get_object()
            context.update({"data": self.serializer_class(instance).data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="The endpoint handles removing  user account"
    )
    def destroy(self, request, *args, **kwargs):
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            instance.delete()
            context.update({"message": "Deleted successfully"})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])
