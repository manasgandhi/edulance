from django.urls import path, include
from . import views

app_name = "collaborate"

urlpatterns = [
    
    path("", views.home, name="collaboration_list"),
]
