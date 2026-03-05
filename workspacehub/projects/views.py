from django.shortcuts import redirect
from .models import Project
from django.views.generic import CreateView, ListView, DetailView
from .forms import ProjectForm, AttachmentForm
from tasks.forms import  TaskUpdateForm
from django.urls import reverse_lazy
from notifications.task import create_notification
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment
from django.core.paginator import Paginator
from comments.forms import CommentForm
from django.contrib import messages
from tasks.forms import TaskAddForm
# Create your views here.
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_create.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
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
            team_members = list(project.team.members.exclude(id=project.owner.id))
            
            def enqueue():
         
                for member in team_members:
                    recipient_name = member.username
                    # Use .delay() to send to Celery
                    create_notification.delay(actor_username, recipient_name, message, content_type_id, object_id)

            transaction.on_commit(enqueue)
            
        return redirect(self.success_url)
    
class ProjectListView(ListView):
    model = Project
    context_object_name = "projects"
    template_name = "projects/project_list.html"
    paginate_by = 2
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        context['header_text'] = "Projects"
        return context
    
class ProjectNearDueListView(ListView):
    model = Project
    context_object_name = "projects"
    template_name = "projects/project_about_due.html"
    paginate_by = 2
    
    def get_queryset(self):
        return Project.objects.all().due_soon()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        context['header_text'] = "Project Near Due"
        return context
    
class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        object = self.get_object()
        comments = Comment.objects.filter_by_instance(object)
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['header_text'] = "Project detail"
        context['title'] = self.get_object().name
        context['my_company'] = "WorkspaceHub"
        context['description'] = "WorkspaceHub es una plataforma colaborativa de gestión de proyectos"
        
      
        context['page_obj'] = page_obj
        context['comment_form'] = CommentForm()
        context['attachment_form'] = AttachmentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        project = self.get_object()
        content_type = ContentType.objects.get_for_model(project)
        if request.user not  in project.team.members.all():
            messages.warning(request, "You are not a member of this project and you cannot comment")
            return self.get(request, *args, **kwargs)
        if 'comment_submit' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    comment = form.save(commit=False)
                    comment.user = request.user
                    comment.content_type = content_type
                    comment.object_id = project.id
                    
                    comment.save()
                    actor_username = self.request.user.username
                    message = f'{actor_username}, commented on  {project.name}'
                    team_members = list(project.team.members.exclude(id=project.owner.id))
                
                    def enqueue():
                
                        for member in team_members:
                            recipient_name = member.username
                            # Use .delay() to send to Celery
                            create_notification.delay(actor_username, recipient_name, message, content_type.id, project.id)

                    transaction.on_commit(enqueue)
                    
                    messages.success(request, "Comment has been added successfully")
                    return redirect('projects:project-detail', pk=project.pk)
            else:
                messages.warning(request, form.errors.get("comment")[0])
                
        if 'attachment_submit' in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.project = project
                attachment.user = request.user
                attachment.save()
                messages.success(request, "Your file has been uploaded successfully")
                return redirect('projects:project-detail', pk=project.pk)
            else:
                messages.error(request, "Error uploading the file, please try again later")
        return self.get(request, *args, **kwargs) 
    

class KanbanBoardView(DetailView):
    model = Project
    template_name = "projects/kanbanboard.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        # latest notifications
        context = super(KanbanBoardView, self).get_context_data(**kwargs)
        latest_notifications = self.request.user.notifications.unread() 
        project = self.get_object()         
        
        context["latest_notifications"] = latest_notifications[:3]
        context["notification_count"] = latest_notifications.count()
        context["header_text"] = "Kanban Board"
        context["title"] = f"{project.name}'s Kanban Board"
        context["is_kanban"] = True

        # separate tasks by status
        context["backlog_tasks"] = project.tasks.filter(status="Backlog").upcoming()
        context["todo_tasks"] = project.tasks.filter(status="To Do").upcoming()
        context["in_progress_tasks"] = project.tasks.filter(status="In Progress").upcoming()
        context["completed_tasks"] = project.tasks.filter(status="Completed").upcoming()
        context['form'] = TaskUpdateForm()
        # context['task_assignment_form'] = TaskUserAssignmentForm()
        context['taskadd_form'] = TaskAddForm()
        return context
    
    def post(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user not  in project.team.members.all():
            messages.warning(request, "You are not a member of this project and you cannot add tasks")
            return self.get(request, *args, **kwargs)
        if 'task_submit' in request.POST:
            task_form = AttachmentForm(request.POST, request.FILES)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.project = project
                task.owner = request.user
                task.status = request.status
                task.save()
                messages.success(request, "Your file has been uploaded successfully")
                return redirect('projects:project-detail', pk=project.pk)
            else:
                messages.error(request, "Error uploading the file, please try again later")
        return self.get(request, *args, **kwargs) 