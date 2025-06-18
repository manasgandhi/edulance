from django.urls import path, include
from . import views

app_name = "users"

urlpatterns = [
    # Web interface URLs
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    # AJAX endpoints for web interface
    path("update-profile/", views.ProfileUpdateView.as_view(), name="update_profile"),
    # OAuth callback
    path(
        "oauth/google/callback/",
        views.google_oauth_callback,
        name="google_oauth_callback",
    ),
    # API endpoints
    path("upload_resume/", views.upload_resume, name="upload_resume"),
]
