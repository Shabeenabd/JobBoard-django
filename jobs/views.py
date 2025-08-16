from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Job, JobApplication, UserProfile
from .forms import CustomUserCreationForm, JobApplicationForm, JobForm


def home(request):
    recent_jobs = Job.objects.filter(is_active=True)[:6]
    total_jobs = Job.objects.filter(is_active=True).count()
    total_companies = Job.objects.filter(is_active=True).values('company').distinct().count()
    
    return render(request, 'home.html', {
        'recent_jobs': recent_jobs,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    
    search_query = request.GET.get('search')
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)
    
    job_type = request.GET.get('job_type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'search_query': search_query,
        'job_type': job_type,
        'location': location,
        'job_types': Job.JOB_TYPES,
    })

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    user_applied = False
    
    if request.user.is_authenticated:
        user_applied = JobApplication.objects.filter(
            job=job, applicant=request.user
        ).exists()
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'user_applied': user_applied,
    })

@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Check if user already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    
    # Check if user is a job seeker
    try:
        profile = request.user.userprofile
        if profile.user_type != 'job_seeker':
            messages.error(request, 'Only job seekers can apply for jobs.')
            return redirect('job_detail', pk=pk)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile.')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', pk=pk)
    else:
        # Pre-fill form with user data
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': getattr(request.user.userprofile, 'phone', ''),
        }
        form = JobApplicationForm(initial=initial_data)
    
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

@login_required
def post_job(request):
    # Check if user is a recruiter
    try:
        profile = request.user.userprofile
        if profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can post jobs.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile.')
        return redirect('home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        # Pre-fill company name from profile
        initial_data = {'company': request.user.userprofile.company_name}
        form = JobForm(initial=initial_data)
    
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def recruiter_dashboard(request):
    # Check if user is a recruiter
    try:
        profile = request.user.userprofile
        if profile.user_type != 'recruiter':
            messages.error(request, 'Access denied.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile.')
        return redirect('home')
    
    jobs = Job.objects.filter(posted_by=request.user).annotate(
        application_count=Count('applications')
    )
    
    total_jobs = jobs.count()
    active_jobs = jobs.filter(is_active=True).count()
    total_applications = JobApplication.objects.filter(
        job__posted_by=request.user
    ).count()
    
    return render(request, 'jobs/recruiter_dashboard.html', {
        'jobs': jobs,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
    })

@login_required
def job_applications(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk, posted_by=request.user)
    applications = JobApplication.objects.filter(job=job)
    
    return render(request, 'jobs/applications.html', {
        'job': job,
        'applications': applications,
    })