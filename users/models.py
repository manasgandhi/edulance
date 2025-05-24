# from django.db import models
# from django.contrib.auth.models import User


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     skills = models.TextField(blank=True)
#     bio = models.TextField(blank=True)


# class Project(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     skills = models.TextField()
#     github_link = models.URLField()
#     created_at = models.DateTimeField(auto_now_add=True)


# class Attachment(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     file = models.FileField(upload_to="attachments/")


# class Application(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     fit_score = models.IntegerField()
#     applied_at = models.DateTimeField(auto_now_add=True)


# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.TextField()
#     applicant = models.ForeignKey(
#         User, related_name="applicant_notifications", on_delete=models.CASCADE
#     )
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _


class Skill(models.Model):
    """Model for storing user skills"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Extended User model to support additional fields and OAuth"""

    # User profile fields
    # profile_picture = models.ImageField(
    #     upload_to="profile_pictures/", null=True, blank=True
    # )
    bio = models.TextField(blank=True, null=True)

    # Social profiles
    github_profile = models.URLField(
        max_length=255, blank=True, null=True, validators=[URLValidator()]
    )

    # Skills - Many-to-Many relationship with Skill model
    skills = models.ManyToManyField(Skill, blank=True, related_name="users")

    # User ratings
    # Rating will be populated later, but we're adding the field now
    # rating = models.FloatField(default=0.0, null=True, blank=True)

    # OAuth related fields
    is_oauth_user = models.BooleanField(default=False)
    oauth_provider = models.CharField(max_length=20, blank=True, null=True)
    oauth_uid = models.CharField(max_length=255, blank=True, null=True)

    # Email verification
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)

    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True
    )

    # Additional timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username
