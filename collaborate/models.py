from django.db import models
from users.models import User, Skill  
from django.db.models import JSONField

class CollaborationPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaboration_posts')
    title = models.CharField(max_length=200)
    description = models.TextField()

    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('learning', 'Learning'),
            ('hackathon', 'Hackathon'),
            ('group_study', 'Group Study'),
            ('project', 'Project'),
        ]
    )

    # required_skills = models.ManyToManyField(Skill, related_name='collaboration_posts', blank=True)
    required_skills = models.JSONField(blank=True, null=True)


    is_active = models.BooleanField(default=True)
    deadline = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
