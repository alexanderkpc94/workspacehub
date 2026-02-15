from django.shortcuts import render
from django.views import View
from projects.models import Project
from tasks.models import Task
from .models import Profile
from notifications.models import Notification
# class DashboardView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'accounts/dashboard.html')
    
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        latest_projects = Project.objects.all()[:5] # Get the latest 5 projects
        latest_tasks = Task.objects.all()[:5]
        latest_members = Profile.objects.all()[:8] # Get the latest 5 members
        context = {}
        context['latest_projects'] = latest_projects
        latest_notifications = Notification.objects.for_user(request.user)
        context['latest_notifications'] = latest_notifications[:3]
        context['latest_tasks'] = latest_tasks
        context['latest_members'] = latest_members
        return render(request, 'accounts/dashboard.html', context)
    
                