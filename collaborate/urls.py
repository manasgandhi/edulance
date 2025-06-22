from django.urls import path, include
from . import views

app_name = "collaborate"

urlpatterns = [
    path("", views.home, name="collaboration_list"),
    path("create/", views.create_post, name="create_post"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("join/<int:post_id>/", views.join_team, name="join_team"),
]