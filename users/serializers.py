from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.html import escape
from .models import User, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_picture",
            "bio",
            "github_profile",
            "skills",
            "phone_number",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        # Clean inputs to prevent XSS
        for field in ["username", "first_name", "last_name", "email"]:
            if field in attrs:
                attrs[field] = escape(attrs[field])

        return attrs

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        if not username and not email:
            raise serializers.ValidationError(
                "Please provide either username or email to login."
            )

        # Clean inputs to prevent XSS
        if username:
            attrs["username"] = escape(username)
        if email:
            attrs["email"] = escape(email)

        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "bio",
            "github_profile",
            "phone_number",
            "profile_picture",
            "current_password",
            "new_password",
            "confirm_new_password",
        ]

    def validate(self, attrs):
        # Clean text inputs to prevent XSS
        for field in ["first_name", "last_name", "bio", "github_profile"]:
            if field in attrs:
                attrs[field] = escape(attrs[field])

        # Check if user is trying to update password
        if "new_password" in attrs:
            if not attrs.get("current_password"):
                raise serializers.ValidationError(
                    {
                        "current_password": "Current password is required to set a new password."
                    }
                )

            if not self.instance.check_password(attrs.get("current_password")):
                raise serializers.ValidationError(
                    {"current_password": "Current password is incorrect."}
                )

            if attrs.get("new_password") != attrs.get("confirm_new_password"):
                raise serializers.ValidationError(
                    {"new_password": "New password fields didn't match."}
                )

            try:
                validate_password(attrs.get("new_password"), self.instance)
            except ValidationError as e:
                raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs

    def update(self, instance, validated_data):
        # Remove password fields from validated_data

        # Update instance with remaining validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
