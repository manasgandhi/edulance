# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.home, name="home"),
#     path("register/", views.register, name="register"),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

app_name = "users"

# API Router
router = DefaultRouter()
router.register(r"api/users", api_views.UserAPIViewSet)
router.register(r"api/skills", api_views.SkillViewSet)

urlpatterns = [
    # Web interface URLs
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "verify-email/<str:uidb64>/<str:token>/",
        views.verify_email_view,
        name="verify_email",
    ),
    # AJAX endpoints for web interface
    path("update-profile/", views.ProfileUpdateView.as_view(), name="update_profile"),
    path(
        "change-password/", views.PasswordChangeView.as_view(), name="change_password"
    ),
    # OAuth callback
    path(
        "oauth/google/callback/",
        views.google_oauth_callback,
        name="google_oauth_callback",
    ),
    # API endpoints
    path("", include(router.urls)),
    path(
        "api/auth/login/",
        api_views.UserAPIViewSet.as_view({"post": "login"}),
        name="api_login",
    ),
    path(
        "api/auth/logout/",
        api_views.UserAPIViewSet.as_view({"post": "logout"}),
        name="api_logout",
    ),
    path(
        "api/auth/me/", api_views.UserAPIViewSet.as_view({"get": "me"}), name="api_me"
    ),
    path(
        "api/auth/verify-email/",
        api_views.UserAPIViewSet.as_view({"post": "verify_email"}),
        name="api_verify_email",
    ),
]
