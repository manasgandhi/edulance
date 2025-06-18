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
logger = logging.getLogger("django")


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

                if not skill_name:
                    continue

                try:
                    skill_obj = Skill.objects.get(id=skill_id)
                    new_skill_ids.append(skill_obj.id)
                except (Skill.DoesNotExist, ValueError):
                    continue

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
