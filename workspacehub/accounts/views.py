from django.shortcuts import render, redirect
from django.views import View
from projects.models import Project
from tasks.models import Task
from .models import Profile
from teams.models import Team
from .forms import RegisterForm
from django.views.generic import ListView
from django.contrib.auth.decorators import login_not_required
from django.contrib import messages

# class DashboardView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'accounts/dashboard.html')


# user registration
@login_not_required
def RegisterView(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration is successful")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form':form})
    
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        latest_projects = Project.objects.all() # Get the latest 5 projects
        latest_tasks = Task.objects.all()
        latest_members = Profile.objects.all() # Get the latest 5 members
        context = {}
        context['latest_projects'] = latest_projects[:5]
        context['number_of_projects'] = latest_projects.count()
        context['number_of_notifications'] = 0
        # if request.user.is_authenticated:
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
    
class MembersListView(ListView):
    model = Profile
    context_object_name = "members"
    template_name = "accounts/profile_list.html"
    paginate_by = 9
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        context['header_text'] = "Projects"
        return context               