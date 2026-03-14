"""
Vistas de la aplicación projects.

Contiene las vistas para crear, listar, ver detalles y el tablero Kanban de proyectos.
"""

from django.shortcuts import redirect
from .models import Project
# CreateView: vista genérica para crear objetos desde formularios
# ListView: vista genérica para listar objetos con paginación
# DetailView: vista genérica para ver un objeto específico
from django.views.generic import CreateView, ListView, DetailView
from .forms import ProjectForm, AttachmentForm
from tasks.forms import  TaskUpdateForm
from django.urls import reverse_lazy
# create_notification es una tarea de Celery para enviar notificaciones asíncronas
from notifications.task import create_notification
# transaction.atomic asegura que las operaciones se ejecuten todas o ninguna
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment
from django.core.paginator import Paginator
from comments.forms import CommentForm
from django.contrib import messages
from tasks.forms import TaskAddForm, TaskUpdateForm
# Create your views here.


class ProjectCreateView(CreateView):
    """
    Vista para crear un nuevo proyecto.
    
    Hereda de CreateView que proporciona:
    - GET: muestra el formulario
    - POST: procesa el formulario y crea el proyecto
    
    Usa transaction.atomic para asegurar que el proyecto y las notificaciones
    se procesen correctamente.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_create.html'
    success_url = reverse_lazy('accounts:dashboard')  # Redirect después de crear
    
    def get_context_data(self, **kwargs):
        """
        Añade notificaciones al contexto de la plantilla.
        
        ¿Por qué sobrescribir este método?
        - Las notificaciones son requeridas en el header de todas las páginas.
        - Permite mantener un diseño consistente sin repetir código.
        """
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        context['header_text'] = "Project Add"
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario cuando es válido.
        
        ¿Por qué sobrescribir en lugar de usar el comportamiento por defecto?
        - Necesitamos establecer el owner (usuario actual) antes de guardar.
        - queremos enviar notificaciones a los miembros del equipo.
        
        transaction.atomic garantiza que:
        - Si falla algo (ej: notificación), se hace rollback del proyecto.
        - Evita proyectos huérfanos sin notificaciones.
        """
        with transaction.atomic():
            # Guardamos el proyecto pero sin commit (no entra a la DB todavía)
            project = form.save(commit=False)
            project.owner = self.request.user  # El usuario que está logueado
            project.save()
            
            # Prepare data for notification
            actor_username = self.request.user.username
            message = f'New project, {project.name} has been created.'
            # ContentType identifica el tipo de objeto para el sistema de notificaciones
            content_type_id = ContentType.objects.get_for_model(Project).id
            object_id = str(project.id) # Ensure ID is string for serialization
            
            # Get team members ID list to avoid query issues inside potential future async closures
            # Although 'members.all()' is evaluated when iterated
            # Excluimos al owner para no enviarle notificación a sí mismo
            team_members = list(project.team.members.exclude(id=project.owner.id))
            
            def enqueue():
                """
                Función que se ejecuta después de que la transacción commit exitosamente.
                
                ¿Por qué usar transaction.on_commit?
                - Las notificaciones se envían SOLO si el proyecto se guardó correctamente.
                - Evita enviar notificaciones de proyectos que fallaron.
                - Mantiene la consistencia de datos.
                """
                for member in team_members:
                    recipient_name = member.username
                    # Use .delay() to send to Celery
                    # .delay() encola la tarea para ejecución asíncrona
                    # No bloquea la respuesta HTTP mientras envía emails
                    create_notification.delay(actor_username, recipient_name, message, content_type_id, object_id)

            transaction.on_commit(enqueue)
            
        return redirect(self.success_url)
    

class ProjectListView(ListView):
    """
    Vista de lista para mostrar todos los proyectos.
    
    Pagina los resultados (2 por página) para mejor rendimiento y UX.
    """
    model = Project
    context_object_name = "projects"  # Nombre en el template: {% for project in projects %}
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
    """
    Vista para mostrar proyectos próximos a vencer (dentro de 2 días).
    
    Usa el método due_soon() del Manager personalizado.
    """
    model = Project
    context_object_name = "projects"
    template_name = "projects/project_about_due.html"
    paginate_by = 2
    
    def get_queryset(self):
        """Filtra proyectos que vencen pronto."""
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
    """
    Vista de detalle para ver un proyecto específico.
    
    Muestra información del proyecto, comentarios y permite agregar archivos.
    """
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"  # Nombre en template: {{ project.name }}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        # Obtenemos los comentarios asociados a este proyecto
        object = self.get_object()
        comments = Comment.objects.filter_by_instance(object)
        
        # Paginación de comentarios (5 por página)
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['header_text'] = "Project detail"
        context['title'] = self.get_object().name
        context['my_company'] = "WorkspaceHub"
        context['description'] = "WorkspaceHub es una plataforma colaborativa de gestión de proyectos"
        
        # Objetos para el template
        context['page_obj'] = page_obj
        context['comment_form'] = CommentForm()
        context['attachment_form'] = AttachmentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Maneja las solicitudes POST para comentarios y adjuntos.
        
        ¿Por qué sobrescribir post() en lugar de usar una vista separada?
        - Mantiene la misma URL para ver el proyecto y agregar contenido.
        - Simplifica la navegación del usuario.
        - Un solo endpoint para diferentes acciones.
        """
        project = self.get_object()
        content_type = ContentType.objects.get_for_model(project)
        
        # Verificación de permisos - solo miembros del equipo pueden comentar
        if request.user not in project.team.members.all():
            messages.warning(request, "You are not a member of this project and you cannot comment")
            return self.get(request, *args, **kwargs)
        
        # Procesar comentario
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
                # Mostrar el primer error del formulario
                messages.warning(request, form.errors.get("comment")[0])
                
        # Procesar archivo adjunto
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
    """
    Vista del tablero Kanban para un proyecto.
    
    Muestra las tareas organizadas por columnas según su estado:
    - Backlog: tareas pendientes
    - To Do: tareas por hacer
    - In Progress: tareas en progreso
    - Completed: tareas terminadas
    
    Permite arrastrar tareas entre columnas (AJAX).
    """
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
        # Filtra las tareas del proyecto por su estado
        # .upcoming() asegura que solo muestre tareas vigentes (no vencidas)
        context["backlog_tasks"] = project.tasks.filter(status="Backlog").upcoming()
        context["todo_tasks"] = project.tasks.filter(status="To Do").upcoming()
        context["in_progress_tasks"] = project.tasks.filter(status="In Progress").upcoming()
        context["completed_tasks"] = project.tasks.filter(status="Completed").upcoming()
        context['form'] = TaskUpdateForm(prefix='edit')
        # context['task_assignment_form'] = TaskUserAssignmentForm()
        context['taskadd_form'] = TaskAddForm()
     
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Maneja la creación de tareas desde el kanban.
        
        Nota: Hay un bug potencial aquí - usa AttachmentForm en lugar de TaskAddForm.
        Esto podría causar errores al intentar crear tareas desde el kanban.
        """
        project = self.get_object()
        if request.user not  in project.team.members.all():
            messages.warning(request, "You are not a member of this project and you cannot add tasks")
            return self.get(request, *args, **kwargs)
        if 'task_submit' in request.POST:
            # Bug: Debería usar TaskAddForm, no AttachmentForm
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