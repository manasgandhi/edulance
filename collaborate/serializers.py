
from rest_framework import serializers
from .models import CollaborationPost
from users.serializers import SkillSerializer
from users.models import Skill

class CollaborationPostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    activity_type_display = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    required_skills = SkillSerializer(many=True, read_only=True)
    skills = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = CollaborationPost
        fields = [
            'id', 'user', 'title', 'description', 'activity_type', 
            'activity_type_display', 'required_skills', 'skills', 
            'deadline', 'is_active', 'created_at', 'updated_at', 'is_owner'
        ]

    def get_user(self, obj):
        return {
            'username': obj.user.username,
            'full_name': obj.user.get_full_name(),
            'email': obj.user.email
        }

    def get_activity_type_display(self, obj):
        return obj.get_activity_type_display()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request.user == obj.user if request else False

    def validate(self, data):
        if not data.get('title') or not data.get('description') or not data.get('activity_type'):
            raise serializers.ValidationError("Title, description, and activity type are required.")
        
        return data

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])  # Extract skills data
        post = CollaborationPost.objects.create(**validated_data)  # Create post
        if skills_data:
            skills = Skill.objects.filter(id__in=skills_data)  # Fetch Skill objects
            post.required_skills.set(skills)  # Set ManyToMany relationship
        return post
