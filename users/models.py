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

    bio = models.TextField(blank=True, null=True)

    # Social profiles
    github_profile = models.URLField(
        max_length=255, blank=True, null=True, validators=[URLValidator()]
    )

    skills = models.ManyToManyField(Skill, blank=True, related_name="users")

    # User ratings
    # Rating will be populated later, but we're adding the field now
    # rating = models.FloatField(default=0.0, null=True, blank=True)

    # OAuth related fields

    oauth_provider = models.CharField(max_length=20, blank=True, null=True)
    oauth_uid = models.CharField(max_length=255, blank=True, null=True)

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

    # Make username and password optional
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username
