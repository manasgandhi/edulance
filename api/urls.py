from django.urls import path, include
from .views import (
    UpdateSkillsAPIView,
)

app_name = "api"

urlpatterns = [
    # Include User API endpoints
    path("", include("users.urls")),
]
