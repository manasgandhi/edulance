from django.db import models
from django.utils import timezone
from users.models import User, Skill


class CollaborationPost(models.Model):
    ACTIVITY_TYPES = (
        ("learning", "Learning"),
        ("hackathon", "Hackathon"),
        ("project", "Project"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="collaboration_posts"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    applicants = models.ManyToManyField(User, related_name="applied_posts", blank=True)
    required_skills = models.ManyToManyField(Skill, related_name="posts", blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_activity_type_display(self):
        return dict(self.ACTIVITY_TYPES).get(self.activity_type, self.activity_type)
