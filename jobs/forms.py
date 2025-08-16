from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, JobApplication, Job

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES, required=True)
    company_name = forms.CharField(max_length=200, required=False, 
                                   help_text="Required for recruiters only")
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,  
                user_type=self.cleaned_data["user_type"],
                company_name=self.cleaned_data.get("company_name", ""),
                phone=self.cleaned_data.get("phone", "")
            )
        return user

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'description', 'requirements', 
                  'location', 'job_type', 'salary_range']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone', 'resume_text', 'cover_letter']
        widgets = {
            'resume_text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste your resume or experience details here...'}),
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a brief cover letter (optional)...'}),
        }