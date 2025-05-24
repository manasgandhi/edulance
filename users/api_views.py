import logging
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from .models import User, Skill
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileUpdateSerializer,
    SkillSerializer,
)

logger = logging.getLogger(__name__)


class UserAPIViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        elif self.action == "login":
            return UserLoginSerializer
        elif self.action == "update" or self.action == "partial_update":
            return UserProfileUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ["create", "login", "verify_email"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Register a new user with email and password"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate verification token
            token = str(uuid.uuid4())
            user.verification_token = token
            user.save()

            # Send verification email
            self.send_verification_email(user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": tokens,
                    "message": "User registered successfully. Please verify your email.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def login(self, request):
        """Login user and return JWT token"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            # Find user by username or email
            if username:
                user = authenticate(username=username, password=password)
            else:
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user:
                login(request, user)

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                tokens = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }

                return Response(
                    {
                        "user": UserSerializer(user).data,
                        "tokens": tokens,
                        "message": "Login successful",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def logout(self, request):
        """Logout user"""
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def verify_email(self, request):
        """Verify user email with token"""
        uid = request.data.get("uid")
        token = request.data.get("token")

        if not uid or not token:
            return Response(
                {"error": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

            if user.verification_token == token:
                user.email_verified = True
                user.verification_token = None
                user.save()
                return Response(
                    {"message": "Email verified successfully"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": "Invalid verification token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
            )

    def send_verification_email(self, user):
        """Send email verification link to user"""
        try:
            current_site = "edulance.example.com"  # Replace with your domain
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = user.verification_token
            mail_subject = "Activate your Edulance account"

            message = render_to_string(
                "users/email_verification.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": uid,
                    "token": token,
                },
            )

            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = "html"
            email.send()

        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for skills (read-only)"""

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
