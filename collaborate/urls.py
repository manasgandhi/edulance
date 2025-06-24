from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import SkillListView
app_name = 'collaborate'

router = DefaultRouter()
router.register(r'posts', views.CollaborationPostViewSet, basename='post')

urlpatterns = [
    path('', views.home, name='collaboration_list'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('api/', include(router.urls)),
    path('api/skills/', SkillListView.as_view(), name='skill_list'),
]