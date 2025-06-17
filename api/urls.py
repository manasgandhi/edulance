from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    # PasswordResetRequestAPIView,
    # PasswordResetConfirmAPIView,
    # ChangePasswordAPIView,
    UpdateSkillsAPIView,
)

app_name = "api"

urlpatterns = [
    # JWT Token endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Include User API endpoints
    path("", include("users.urls")),
    # ]
    # app_name = 'users'
    # urlpatterns = [
    # path(
    #     "password_reset/", PasswordResetRequestAPIView.as_view(), name="password_reset"
    # ),
    # path(
    #     "password_reset_confirm/<str:token>/",
    #     PasswordResetConfirmAPIView.as_view(),
    #     name="password_reset_confirm",
    # ),
    # path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
]
