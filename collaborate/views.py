from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CollaborationPost
from .serializers import CollaborationPostSerializer
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from users.models import Skill
from users.serializers import SkillSerializer
from common.tasks import send_asynchronous_email_task
import json


@login_required
def home(request):
    user_skills = request.user.skills.all()
    user_skill_id = set()
    for skill in user_skills:
        user_skill_id.add(skill.id)

    all_posts = CollaborationPost.objects.filter(is_active=True).prefetch_related(
        "required_skills"
    )

    post_match_list = []
    for post in all_posts:
        match_skill_count = 0
        for skill in post.required_skills.all():
            if skill.id in user_skill_id:
                match_skill_count += 1
        post_match_list.append((post, match_skill_count))

    # Sort posts by match count in descending order
    sorted_posts = [
        post for post, _ in sorted(post_match_list, key=lambda x: x[1], reverse=True)
    ]

    # Categorize sorted posts by activity type
    posts_by_type = {
        "learning": [p for p in sorted_posts if p.activity_type == "learning"],
        "hackathon": [p for p in sorted_posts if p.activity_type == "hackathon"],
        "project": [p for p in sorted_posts if p.activity_type == "project"],
    }

    posts_counts = {
        "learning": len(posts_by_type["learning"]),
        "hackathon": len(posts_by_type["hackathon"]),
        "project": len(posts_by_type["project"]),
    }

    skills = Skill.objects.all()
    skills_serialized = SkillSerializer(skills, many=True).data
    skills_data = [
        {"id": skill["id"], "text": skill["name"]} for skill in skills_serialized
    ]
    skills_json = json.dumps(skills_data)
    context = {
        "posts_by_type": posts_by_type,
        "posts_counts": posts_counts,
        "total_posts": all_posts.count(),
        "skills_json": skills_json,
    }

    return render(request, "collaborate/collaboration.html", context)


@login_required
def post_detail(request, post_id):
    try:
        post = CollaborationPost.objects.get(id=post_id, is_active=True)
        skills = SkillSerializer(
            Skill.objects.only("id", "name", "description").all(), many=True
        ).data
        context = {"post": post, "skills": skills}
        return render(request, "collaborate/post_detail.html", context)
    except CollaborationPost.DoesNotExist:
        return render(
            request, "collaborate/collaboration.html", {"error": "Post not found"}
        )


class CollaborationPostViewSet(viewsets.ModelViewSet):
    queryset = CollaborationPost.objects.filter(is_active=True)
    serializer_class = CollaborationPostSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        activity_type = self.request.query_params.get("activity_type")
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        return queryset.order_by("-created_at")

    def destroy(self, request, *args, **kwargs):
        """
        Custom delete method with validation
        """
        try:
            instance = self.get_object()

            # Check if user owns the post
            if instance.user != request.user:
                return Response(
                    {"detail": "You do not have permission to delete this post."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if there are applicants (Might Add In Future)
            # applicants_count = instance.applicants.count()
            # if applicants_count > 0:
            #     for email in applicants_emails:
            #         subject = f"Collaboration Post Deleted: {instance.title}"
            #         message = f"""
            #         Hi there,

            #         The collaboration post "{instance.title}" that you applied to has been deleted by the creator.

            #         We apologize for any inconvenience this may cause.

            #         Best regards,
            #         Edulance Team
            #         """
            #         try:
            #             send_asynchronous_email_task(subject, message, email)
            #         except Exception as email_error:
            #             logger.error(f"Failed to send deletion notification to {email}: {email_error}")

            instance.delete()

            return Response(
                {"detail": "Post deleted successfully."}, status=status.HTTP_200_OK
            )

        except CollaborationPost.DoesNotExist:
            return Response(
                {"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": "An error occurred while deleting the post."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user
            if post.user == user:
                return Response(
                    {"error": "You cannot join your own post"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Implement your join logic here
            if post.applicants.filter(id=user.id).exists():
                return Response({"message": "You have already joined this post."})

            post.applicants.add(user)

            # Email to post creator
            subject = f"New Applicant for Your Collaboration: {post.title}"
            message = f"""
                Hi {post.user.username},

                {user.username} has joined your collaboration post: "{post.title}".

                Contact them at: {user.email}

                Regards,
                Edulance
                """
            send_asynchronous_email_task(subject, message, post.user.email)

            return Response(
                {
                    "message": f'Interest shown in "{post.title}". Contact details will be shared soon!'
                }
            )
        except CollaborationPost.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )


class SkillListView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        print(skills)
        return Response({"results": serializer.data})
