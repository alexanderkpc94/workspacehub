from django.shortcuts import redirect
from .models import Project
from django.views.generic import CreateView
from .forms import ProjectForm
from django.urls import reverse_lazy
from notifications.task import create_notification
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
# Create your views here.
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_create.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        if self.request.user.is_authenticated:
            latest_notifications = self.request.user.notifications.unread()
            context['latest_notifications'] = latest_notifications[:3]
            context['number_of_notifications'] = latest_notifications.count()
        
        context['header_text'] = "Project Add"
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            project = form.save(commit=False)
            project.owner = self.request.user
            project.save()
            
            # Prepare data for notification
            actor_username = self.request.user.username
            message = f'New project, {project.name} has been created.'
            content_type_id = ContentType.objects.get_for_model(Project).id
            object_id = str(project.id) # Ensure ID is string for serialization
            
            # Get team members ID list to avoid query issues inside potential future async closures
            # Although 'members.all()' is evaluated when iterated
            team_members = list(project.team.members.all())
            
            def enqueue():
         
                for member in team_members:
                    recipient_name = member.username
                    # Use .delay() to send to Celery
                    create_notification.delay(actor_username, recipient_name, message, content_type_id, object_id)

            transaction.on_commit(enqueue)
            
        return redirect(self.success_url)