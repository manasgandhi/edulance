from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
import logging
import json
from users.models import Skill

User = get_user_model()
logger = logging.getLogger(__name__)


# class PasswordResetRequestAPIView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         if not email:
#             return Response(
#                 {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND
#             )

#         # Generate token and UID
#         token_generator = PasswordResetTokenGenerator()
#         token = token_generator.make_token(user)
#         uid = urlsafe_base64_encode(force_bytes(user.pk))

#         # Build reset URL
#         reset_url = (
#             request.build_absolute_uri(
#                 reverse("users:password_reset_confirm", kwargs={"token": token})
#             )
#             + f"?uid={uid}"
#         )

#         # Send email
#         try:
#             send_mail(
#                 subject="Edulance Password Reset",
#                 message=f"Click the link to reset your password: {reset_url}",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[email],
#                 fail_silently=False,
#             )
#             return Response(
#                 {"success": "Password reset link sent to your email."},
#                 status=status.HTTP_200_OK,
#             )
#         except Exception as e:
#             logger.error(f"Failed to send password reset email: {str(e)}")
#             return Response(
#                 {"error": "Failed to send email. Please try again."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# class PasswordResetConfirmAPIView(APIView):
#     def post(self, request):
#         token = request.data.get("token")
#         uid = request.data.get("uid")
#         new_password = request.data.get("new_password")
#         confirm_password = request.data.get("confirm_password")

#         if not all([token, uid, new_password, confirm_password]):
#             return Response(
#                 {"error": "All fields are required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if new_password != confirm_password:
#             return Response(
#                 {"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             uid = force_str(urlsafe_base64_decode(uid))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             return Response(
#                 {"error": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         token_generator = PasswordResetTokenGenerator()
#         if not token_generator.check_token(user, token):
#             return Response(
#                 {"error": "Invalid or expired token."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Set new password
#         try:
#             user.set_password(new_password)
#             user.save()
#             return Response(
#                 {"success": "Password reset successfully. You can now log in."},
#                 status=status.HTTP_200_OK,
#             )
#         except Exception as e:
#             logger.error(f"Failed to reset password: {str(e)}")
#             return Response(
#                 {"error": "Failed to reset password. Please try again."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# class ChangePasswordAPIView(APIView):
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Authentication required."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#         current_password = request.data.get("current_password")
#         new_password = request.data.get("new_password")
#         confirm_password = request.data.get("confirm_password")

#         if not all([current_password, new_password, confirm_password]):
#             return Response(
#                 {"error": "All fields are required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if new_password != confirm_password:
#             return Response(
#                 {"error": "New passwords do not match."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user = request.user
#         if not user.check_password(current_password):
#             return Response(
#                 {"error": "Invalid current password."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Basic password strength validation
#         if len(new_password) < 8:
#             return Response(
#                 {"error": "New password must be at least 8 characters long."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             user.set_password(new_password)
#             user.save()
#             return Response(
#                 {"success": "Password updated successfully."}, status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             logger.error(f"Failed to update password: {str(e)}")
#             return Response(
#                 {"error": "Failed to update password. Please try again."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


class UpdateSkillsAPIView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            skills_data = json.loads(request.data.get("skills", "[]"))
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid skills data."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(skills_data, list):
            return Response(
                {"error": "Skills must be a list."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        new_skill_ids = []

        try:
            for skill in skills_data:
                skill_id = skill.get("id")
                skill_name = skill.get("name")
                is_new = skill.get("isNew", False)

                if not skill_name:
                    continue

                if is_new:
                    # Create new skill if it doesn't exist
                    # skill_obj, created = Skill.objects.get_or_create(
                    #     name=skill_name.strip(), defaults={"description": ""}
                    # )
                    # new_skill_ids.append(skill_obj.id)
                    pass
                else:
                    # Validate existing skill
                    try:
                        skill_obj = Skill.objects.get(id=skill_id)
                        new_skill_ids.append(skill_obj.id)
                    except (Skill.DoesNotExist, ValueError):
                        continue

            # Update user's skills
            user.skills.clear()  # Remove existing skills
            user.skills.add(*new_skill_ids)  # Add new/selected skills

            return Response(
                {"success": "Skills updated successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Failed to update skills: {str(e)}")
            return Response(
                {"error": "Failed to update skills. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
