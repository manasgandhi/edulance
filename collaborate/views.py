from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CollaborationPost
from .serializers import CollaborationPostSerializer
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from .models import Skill
from .serializers import SkillSerializer
import json

@login_required
def home(request):
    all_posts = CollaborationPost.objects.filter(is_active=True).order_by('-created_at')
    posts_by_type = {
        'learning': all_posts.filter(activity_type='learning'),
        'hackathon': all_posts.filter(activity_type='hackathon'),
        'group_study': all_posts.filter(activity_type='group_study'),
        'project': all_posts.filter(activity_type='project'),
    }
    skills = Skill.objects.all()
    # Serialize skills to match Select2 expected format
    skills_serialized = SkillSerializer(skills, many=True).data
    skills_data = [{'id': skill['id'], 'text': skill['name']} for skill in skills_serialized]
    # Convert to JSON
    skills_json = json.dumps(skills_data)
    context = {
        'posts_by_type': posts_by_type,
        'total_posts': all_posts.count(),
        'skills_json': skills_json,
    }
    
    return render(request, "collaborate/collaboration.html", context)

@login_required
def post_detail(request, post_id):
    try:
        post = CollaborationPost.objects.get(id=post_id, is_active=True)
        context = {'post': post}
        return render(request, 'collaborate/post_detail.html', context)
    except CollaborationPost.DoesNotExist:
        return render(request, 'collaborate/collaboration.html', {'error': 'Post not found'})

class CollaborationPostViewSet(viewsets.ModelViewSet):
    queryset = CollaborationPost.objects.filter(is_active=True)
    serializer_class = CollaborationPostSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        try:
            post = self.get_object()
            if post.user == request.user:
                return Response({'error': 'You cannot join your own post'}, status=status.HTTP_400_BAD_REQUEST)
            # Implement your join logic here
            return Response({
                'message': f'Interest shown in "{post.title}". Contact details will be shared soon!'
            })
        except CollaborationPost.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
class SkillListView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        print(skills)
        return Response({'results': serializer.data})