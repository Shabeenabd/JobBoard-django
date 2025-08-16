from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('post_job/', views.post_job, name='post_job'),
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('applications/<int:job_pk>', views.job_applications, name='job_applications'),
    
]