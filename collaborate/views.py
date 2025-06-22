from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    dummy_posts = [
        {
            "title": "AI-Powered Resume Analyzer",
            "description": "Build a tool that uses NLP to analyze and improve resumes submitted by users, giving them recommendations to better match job listings.",
            "skills": ["Python", "NLP", "Flask", "Machine Learning"]
        },
        {
            "title": "Hackathon Submission Platform",
            "description": "Create a lightweight web app where teams can submit their hackathon projects and receive ratings and feedback from mentors and judges.",
            "skills": ["Django", "HTML/CSS", "Bootstrap", "PostgreSQL"]
        },
        {
            "title": "Live Collaboration Whiteboard",
            "description": "Implement a real-time collaborative drawing board with chat support, perfect for team brainstorming during a hackathon.",
            "skills": ["JavaScript", "WebSocket", "Node.js", "Socket.io"]
        },
        {
            "title": "Smart Campus Navigation",
            "description": "Develop a mobile app that helps students navigate campus buildings using AR and provides real-time information about facilities.",
            "skills": ["React Native", "ARKit", "Firebase", "Google Maps API"]
        },
        {
            "title": "Student Marketplace",
            "description": "Create a platform where students can buy, sell, and exchange textbooks, electronics, and other items within their university community.",
            "skills": ["MERN Stack", "PayPal API", "Cloudinary", "JWT"]
        }
    ]
    
    # Debug: Print to console to verify data is being passed
    print("Posts being passed to template:", dummy_posts)
    
    context = {
        "posts": dummy_posts,
        "total_posts": len(dummy_posts)
    }
    
    return render(request, "collaborate/collaboration.html", context)