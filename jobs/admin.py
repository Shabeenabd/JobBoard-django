from django.contrib import admin
from .models import UserProfile, Job, JobApplication

# admin.site.register(UserProfile)
admin.site.register(Job)
admin.site.register(JobApplication)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'company_name']#, 'phone']
    list_filter = ['user_type']
    search_fields = ['user__username', 'company_name']