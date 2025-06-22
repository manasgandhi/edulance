from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import CollaborationPost
import json

def home(request):
    # Get all active collaboration posts
    all_posts = CollaborationPost.objects.filter(is_active=True).order_by('-created_at')
    
    # Organize posts by activity type
    posts_by_type = {
        'learning': all_posts.filter(activity_type='learning'),
        'hackathon': all_posts.filter(activity_type='hackathon'),
        'group_study': all_posts.filter(activity_type='group_study'),
        'project': all_posts.filter(activity_type='project'),
    }
    
    context = {
        'posts_by_type': posts_by_type,
        'total_posts': all_posts.count()
    }
    
    return render(request, "collaborate/collaboration.html", context)

@login_required
def create_post(request):
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            activity_type = request.POST.get('activity_type', '').strip()
            skills_input = request.POST.get('skills', '').strip()
            deadline_str = request.POST.get('deadline', '').strip()
            
            # Validate required fields
            if not all([title, description, activity_type]):
                messages.error(request, 'Title, description, and activity type are required.')
                return redirect('collaborate:collaboration_list')
            
            # Process skills - convert comma-separated string to list
            skills_list = []
            if skills_input:
                skills_list = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
            
            # Process deadline
            deadline = None
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                    deadline = timezone.make_aware(deadline)
                except ValueError:
                    messages.error(request, 'Invalid deadline format.')
                    return redirect('collaborate:collaboration_list')
            
            # Create the post
            post = CollaborationPost.objects.create(
                user=request.user,
                title=title,
                description=description,
                activity_type=activity_type,
                required_skills=skills_list,
                deadline=deadline
            )
            
            # Clear any existing messages to prevent duplicates
            storage = messages.get_messages(request)
            storage.used = True
            
            # Add success message
            messages.success(request, 'Your collaboration post has been created successfully!')
            return redirect('collaborate:collaboration_list')
            
        except Exception as e:
            messages.error(request, f'An error occurred while creating the post: {str(e)}')
            return redirect('collaborate:collaboration_list')
    
    return redirect('collaborate:collaboration_list')

@login_required
def post_detail(request, post_id):
    try:
        post = CollaborationPost.objects.get(id=post_id, is_active=True)
        context = {
            'post': post
        }
        return render(request, 'collaborate/post_detail.html', context)
    except CollaborationPost.DoesNotExist:
        messages.error(request, 'Post not found.')
        return redirect('collaborate:collaboration_list')

@login_required
def join_team(request, post_id):
    # This is a placeholder for join team functionality
    # You can implement the actual logic based on your requirements
    try:
        post = CollaborationPost.objects.get(id=post_id, is_active=True)
        messages.success(request, f'Interest shown in "{post.title}". Contact details will be shared soon!')
        return redirect('collaborate:collaboration_list')
    except CollaborationPost.DoesNotExist:
        messages.error(request, 'Post not found.')
        return redirect('collaborate:collaboration_list')