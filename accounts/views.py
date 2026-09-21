from django.contrib.auth import authenticate

from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializers import RegisterSerializer


# ============================================================
# REGISTER
# ============================================================

@extend_schema(
    request=RegisterSerializer,
    responses={
        201: inline_serializer(
            name="RegisterResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
                "data": serializers.DictField(),
                "errors": serializers.JSONField(allow_null=True),
                "meta": serializers.DictField(),
            },
        ),
        400: OpenApiResponse(
            description="Validation failed"
        ),
    },
)
@api_view(["POST"])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "message": "Registration failed.",
                "data": None,
                "errors": serializer.errors,
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()

    return Response(
        {
            "success": True,
            "message": "User registered successfully.",
            "data": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at,
            },
            "errors": None,
            "meta": {},
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# LOGIN
# ============================================================

@extend_schema(
    request=inline_serializer(
        name="LoginRequest",
        fields={
            "email": serializers.EmailField(),
            "password": serializers.CharField(
                write_only=True
            ),
        },
    ),
    responses={
        200: inline_serializer(
            name="LoginResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
                "data": serializers.DictField(),
                "errors": serializers.JSONField(
                    allow_null=True
                ),
                "meta": serializers.DictField(),
            },
        ),
        400: OpenApiResponse(
            description="Invalid credentials"
        ),
    },
)
@api_view(["POST"])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {
                "success": False,
                "message": "Email and password are required.",
                "data": None,
                "errors": {
                    "credentials": [
                        "Email and password are required."
                    ]
                },
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(
        request=request,
        username=email,
        password=password,
    )

    if user is None:
        return Response(
            {
                "success": False,
                "message": "Invalid email or password.",
                "data": None,
                "errors": {
                    "credentials": [
                        "Invalid email or password."
                    ]
                },
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.status != "ACTIVE" or not user.is_active:
        return Response(
            {
                "success": False,
                "message": "User account is not active.",
                "data": None,
                "errors": {
                    "status": [
                        "Your account is not active."
                    ]
                },
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "success": True,
            "message": "Login successful.",
            "data": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "phone": user.phone,
                    "role": user.role,
                    "status": user.status,
                },
            },
            "errors": None,
            "meta": {},
        },
        status=status.HTTP_200_OK,
    )
# ============================================================
# REFRESH TOKEN
# ============================================================

@extend_schema(
    request=inline_serializer(
        name="RefreshTokenRequest",
        fields={
            "refresh": serializers.CharField(
                write_only=True
            ),
        },
    ),
    responses={
        200: inline_serializer(
            name="RefreshTokenResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
                "data": serializers.DictField(),
                "errors": serializers.JSONField(
                    allow_null=True
                ),
                "meta": serializers.DictField(),
            },
        ),
        400: OpenApiResponse(
            description="Invalid refresh token"
        ),
    },
)
@api_view(["POST"])
def refresh_token_view(request):

    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {
                "success": False,
                "message": "Refresh token is required.",
                "data": None,
                "errors": {
                    "refresh": [
                        "Refresh token is required."
                    ]
                },
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        refresh = RefreshToken(refresh_token)

        return Response(
            {
                "success": True,
                "message": "Access token refreshed successfully.",
                "data": {
                    "access": str(refresh.access_token),
                },
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )

    except TokenError:
        return Response(
            {
                "success": False,
                "message": "Invalid or expired refresh token.",
                "data": None,
                "errors": {
                    "refresh": [
                        "Invalid or expired refresh token."
                    ]
                },
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
# ============================================================
# LOGOUT
# ============================================================

@extend_schema(
    request=inline_serializer(
        name="LogoutRequest",
        fields={
            "refresh": serializers.CharField(
                write_only=True
            ),
        },
    ),
    responses={
        200: inline_serializer(
            name="LogoutResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
                "data": serializers.DictField(),
                "errors": serializers.JSONField(
                    allow_null=True
                ),
                "meta": serializers.DictField(),
            },
        ),
        400: OpenApiResponse(
            description="Invalid or expired refresh token"
        ),
    },
)
@api_view(["POST"])
def logout_view(request):

    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {
                "success": False,
                "message": "Refresh token is required.",
                "data": None,
                "errors": {
                    "refresh": [
                        "Refresh token is required."
                    ]
                },
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        refresh = RefreshToken(refresh_token)
        refresh.blacklist()

        return Response(
            {
                "success": True,
                "message": "Logout successful.",
                "data": {},
                "errors": None,
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )

    except TokenError:
        return Response(
            {
                "success": False,
                "message": "Invalid or expired refresh token.",
                "data": None,
                "errors": {
                    "refresh": [
                        "Invalid or expired refresh token."
                    ]
                },
                "meta": {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )