from django import forms
from .models import CollaborationPost
from django.utils import timezone

class CollaborationPostForm(forms.ModelForm):
    skills = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Python, Django, AI, Machine Learning (comma-separated)'
        }),
        help_text='Enter skills separated by commas. Leave blank if no specific skills are required.'
    )
    
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        help_text='Set a deadline for when you need collaborators or when the project should be completed.'
    )

    class Meta:
        model = CollaborationPost
        fields = ['title', 'description', 'activity_type', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your collaboration post in detail...'
            }),
            'activity_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_skills(self):
        skills_input = self.cleaned_data.get('skills', '')
        if skills_input:
            # Convert comma-separated string to list
            skills_list = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
            return skills_list
        return []

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now():
            raise forms.ValidationError("Deadline must be in the future.")
        return deadline

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set the required_skills field with the processed skills list
        instance.required_skills = self.cleaned_data.get('skills', [])
        if commit:
            instance.save()
        return instance