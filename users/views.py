# from django.shortcuts import render, redirect
# from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm

# # from django.contrib.auth.decorators import login_required
# from django.core.cache import cache
# from django.http import JsonResponse
# from .models import Profile

# # , Project, Attachment, Application, Notification
# # from .tasks import send_application_email
# import json
# from django.http import HttpResponse


# def home(request):
#     # projects = cache.get("projects")
#     # if not projects:
#     #     projects = Project.objects.all()
#     #     cache.set("projects", projects, timeout=300)
#     # return render(request, "home.html", {"projects": projects})
#     return HttpResponse("<h1>hi</h1>")


# def register(request):
#     if request.method == "POST":
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             Profile.objects.create(user=user)
#             login(request, user)
#             return redirect("home")
#     else:
#         form = UserCreationForm()
#     return render(request, "register.html", {"form": form})


import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from social_django.utils import psa

from .models import User, Skill
import uuid
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
    if request.method == "POST":
        # Get form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        # Validate form data
        if not all(
            [username, email, password, confirm_password, first_name, last_name]
        ):
            messages.error(request, "All fields are required.")
            return render(request, "users/register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/register.html")

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "users/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "users/register.html")

        # Create new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            # Generate verification token
            token = str(uuid.uuid4())
            user.verification_token = token
            user.save()

            # Send verification email
            send_verification_email(user)

            messages.success(
                request,
                "Registration successful! Please check your email to verify your account.",
            )
            return redirect("users:login")

        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            messages.error(request, "Registration failed. Please try again later.")

    return render(request, "users/register.html")


@csrf_protect
def login_view(request):
    """User login view"""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect("users:profile")
        else:
            messages.error(request, "Invalid username or password.")

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


def verify_email_view(request, uidb64, token):
    """Email verification view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user.verification_token == token:
            user.email_verified = True
            user.verification_token = None
            user.save()
            messages.success(
                request, "Email verified successfully! You can now log in."
            )
        else:
            messages.error(request, "Invalid verification link.")

        return redirect("users:login")

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid verification link.")
        return redirect("users:login")


@method_decorator(csrf_protect, name="dispatch")
class ProfileUpdateView(View):
    """View for handling AJAX profile updates"""

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            user = request.user

            # Update fields
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


@method_decorator(csrf_protect, name="dispatch")
class PasswordChangeView(View):
    """View for handling password changes"""

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not all([current_password, new_password, confirm_password]):
            return JsonResponse({"error": "All fields are required"}, status=400)

        if new_password != confirm_password:
            return JsonResponse({"error": "New passwords do not match"}, status=400)

        user = request.user
        if not user.check_password(current_password):
            return JsonResponse({"error": "Current password is incorrect"}, status=400)

        user.set_password(new_password)
        user.save()

        # Re-authenticate to prevent logout
        user = authenticate(username=user.username, password=new_password)
        login(request, user)

        return JsonResponse({"success": "Password changed successfully"})


def send_verification_email(user):
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


@psa("social:complete")
def google_oauth_callback(request, backend):
    """Handle Google OAuth callback"""
    if request.user and request.user.is_authenticated:
        # Update OAuth info
        user = request.user
        user.is_oauth_user = True
        user.oauth_provider = "google"
        # OAuth ID should be set by the social auth pipeline
        user.email_verified = True  # Google verifies emails
        user.save()

    return redirect("users:profile")

# @login_required
# def upload_resume(request):
#     if request.method == 'POST' and request.FILES.get('resume'):
#         resume = request.FILES['resume']
#         # user = request.user
#         # user.resume = resume
#         # user.save()
#         data = process_resume_file(resume)
#         print(data)
#         return redirect('users:profile') 
    

#     return render(request, 'users/profile.html')


import tempfile
import os

@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            for chunk in resume_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Process resume using the file path
            extracted_skills = process_resume_file(temp_file_path)
            print(f"Extracted skills: {extracted_skills}")
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
            'skills': skills, 
            'avatar_url': avatar_url,
            'extracted_skills': extracted_skills,  # This will be available in template
            'data': extracted_skills  # Also available as 'data' if you prefer
        }
        
        return render(request, 'users/profile.html', context)

    # If GET request or no file uploaded
    avatar_url = get_user_avatar(request.user)
    skills = Skill.objects.all()
    context = {
        'skills': skills, 
        'avatar_url': avatar_url
    }
    return render(request, 'users/profile.html', context)