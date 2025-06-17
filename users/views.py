import logging
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from social_django.utils import psa

import tempfile
import os


from .models import Skill

from social_django.models import UserSocialAuth


from .resume import process_resume_file


def get_user_avatar(user):
    try:
        social = user.social_auth.get(provider="google-oauth2")
        return social.extra_data["picture"]
    except UserSocialAuth.DoesNotExist:
        return None


logger = logging.getLogger(__name__)


def home_view(request):
    """Home page view"""
    return render(request, "users/home.html")


@csrf_protect
def register_view(request):
    """User registration view"""
    return render(request, "users/register.html")


@csrf_protect
def login_view(request):
    """User login view"""
    form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("users:home")


@login_required
def profile_view(request):
    """User profile view"""
    avatar_url = get_user_avatar(request.user)
    skills = Skill.objects.all()
    return render(
        request, "users/profile.html", {"skills": skills, "avatar_url": avatar_url}
    )


# @login_required
@method_decorator(csrf_protect, name="dispatch")
class ProfileUpdateView(View):
    """View for handling AJAX profile updates"""
    # @login_required
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            user = request.user

            for field in [
                "first_name",
                "last_name",
                "bio",
                "github_profile",
                "phone_number",
            ]:
                if field in request.POST:
                    setattr(user, field, request.POST.get(field))

            # Handle profile picture upload
            if "profile_picture" in request.FILES:
                user.profile_picture = request.FILES["profile_picture"]

            # Handle skills update
            if "skills[]" in request.POST:
                skill_ids = request.POST.getlist("skills[]")
                skills = Skill.objects.filter(id__in=skill_ids)
                user.skills.set(skills)

            user.save()
            return JsonResponse({"success": "Profile updated successfully"})

        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return JsonResponse({"error": str(e)}, status=400)


@psa("social:complete")
def google_oauth_callback(request, backend):
    """Handle Google OAuth callback"""
    if request.user and request.user.is_authenticated:
        # Update OAuth info
        user = request.user
        # user.is_oauth_user = True
        user.oauth_provider = "google"
        # OAuth ID should be set by the social auth pipeline
        # user.email_verified = True  # Google verifies emails
        user.save()

    return redirect("users:profile")


@login_required
def upload_resume(request):
    if request.method == "POST" and request.FILES.get("resume"):
        resume_file = request.FILES["resume"]

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            for chunk in resume_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Process resume using the file path
            extracted_skills = process_resume_file(temp_file_path)
            print(f"Extracted skills: {extracted_skills}")
            extracted_skills = set(skill.strip() for skill in extracted_skills if skill.strip())

            # Get or create Skill objects
            skill_objects = []
            for skill_name in extracted_skills:
                skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                skill_objects.append(skill_obj)

            # Associate with the user (assuming a UserProfile with many-to-many to Skill)
            request.user.skills.set(skill_objects)  # or .add() if you want to keep old ones
            request.user.save()

        except Exception as e:
            print(f"Error processing resume: {e}")
            extracted_skills = []
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)

        # Get all skills for the template
        avatar_url = get_user_avatar(request.user)
        skills = Skill.objects.all()

        # Pass the extracted skills to the template
        context = {
            "skills": skills,
            "avatar_url": avatar_url,
            "extracted_skills": extracted_skills,  # This will be available in template
            "data": extracted_skills,  # Also available as 'data' if you prefer
        }

        return render(request, "users/profile.html", context)

    # If GET request or no file uploaded
    avatar_url = get_user_avatar(request.user)
    skills = Skill.objects.all()
    context = {"skills": skills, "avatar_url": avatar_url}
    return render(request, "users/profile.html", context)
