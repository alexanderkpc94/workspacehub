from django.shortcuts import render
from django.views import View
from projects.models import Project
from tasks.models import Task
from .models import Profile
from teams.models import Team
# class DashboardView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'accounts/dashboard.html')
    
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        latest_projects = Project.objects.all() # Get the latest 5 projects
        latest_tasks = Task.objects.all()
        latest_members = Profile.objects.all() # Get the latest 5 members
        context = {}
        context['latest_projects'] = latest_projects[:5]
        context['number_of_projects'] = latest_projects.count()
        context['number_of_notifications'] = 0
        if request.user.is_authenticated:
            latest_notifications = request.user.notifications.unread()
            context['latest_notifications'] = latest_notifications[:3]
            context['number_of_notifications'] = latest_notifications.count()
        context['projects_near_due_date'] = latest_projects.due_soon()[:5]
        context['number_of_tasks'] = latest_tasks.count()
        context['latest_members'] = latest_members[:8]
        context['number_of_members'] = latest_members.count()
        context['number_of_teams'] = Team.objects.count()
        context['header_text'] = "Dashboard"
        return render(request, 'accounts/dashboard.html', context)
    
                