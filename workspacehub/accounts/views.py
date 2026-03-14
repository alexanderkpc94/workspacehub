"""
Vistas de la aplicación accounts.

Contiene las vistas para el dashboard, lista de miembros y registro de usuarios.
"""

from django.shortcuts import render, redirect
from django.views import View
from projects.models import Project
from tasks.models import Task
from .models import Profile
from teams.models import Team
from .forms import RegisterForm
from django.views.generic import ListView
# login_not_required es el inverso de login_required - permite acceso a usuarios NO autenticados
from django.contrib.auth.decorators import login_not_required
from django.contrib import messages


# class DashboardView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'accounts/dashboard.html')


@login_not_required
def RegisterView(request):
    """
    Vista para el registro de nuevos usuarios.
    
    ¿Por qué usar @login_not_required?
    - Los usuarios nuevos no están autenticados, necesitan acceder a esta página.
    - Si un usuario ya está logueado, podría redirigirlo a su dashboard.
    
    Flujo:
    1. GET: Muestra el formulario de registro vacío.
    2. POST: Procesa los datos del formulario, crea el usuario y redirige al login.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # El formulario ya hace el trabajo de crear el usuario y hashear la contraseña
            user = form.save()
            messages.success(request, "Registration is successful")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form':form})
    

class DashboardView(View):
    """
    Vista principal del dashboard - muestra estadísticas y resumen del sistema.
    
    ¿Por qué una Class-Based View (CBV) en lugar de una función?
    - Las CBVs permiten herencia y reutilización de código (mixins).
    - Separan mejor la lógica de GET y POST con métodos get() y post().
    - Son más fáciles de extender para funcionalidades adicionales.
    
    Datos que proporciona:
    - Proyectos recientes y totales
    - Tareas totales
    - Miembros del sistema
    - Notificaciones no leídas
    - Proyectos próximos a vencer
    """
    def get(self, request, *args, **kwargs):
        latest_projects = Project.objects.all() # Get the latest 5 projects
        latest_tasks = Task.objects.all()
        latest_members = Profile.objects.all() # Get the latest 5 members
        context = {}
        
        # Limitamos a 5 proyectos para no saturar la vista
        context['latest_projects'] = latest_projects[:5]
        context['number_of_projects'] = latest_projects.count()
        context['number_of_notifications'] = 0
        
        # Las notificaciones solo tienen sentido si el usuario está autenticado
        # El modelo de notificaciones usa un manager personalizado (.notifications)
        # if request.user.is_authenticated:
        latest_notifications = request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        # due_soon() es un método personalizado del Project manager
        context['projects_near_due_date'] = latest_projects.due_soon()[:5]
        context['number_of_tasks'] = latest_tasks.count()
        context['latest_members'] = latest_members[:8]
        context['number_of_members'] = latest_members.count()
        context['number_of_teams'] = Team.objects.count()
        context['header_text'] = "Dashboard"
        return render(request, 'accounts/dashboard.html', context)
    

class MembersListView(ListView):
    """
    Vista de lista genérica para mostrar todos los miembros/perfiles.
    
    ¿Por qué usar ListView en lugar de una función?
    - ListView ya proporciona paginación, contexto automático, y plantilla básica.
    - Reduce código repetitivo comparado con escribirlo manualmente.
    - Facilita la personalización mediante sobrescritura de métodos.
    
    Paginación: 9 miembros por página (configurable en el template).
    """
    model = Profile
    context_object_name = "members"  # Nombre en el template: {% for member in members %}
    template_name = "accounts/profile_list.html"
    paginate_by = 9
    

    def get_context_data(self, **kwargs):
        """
        Sobrescribimos el contexto para añadir notificaciones.
        
        ¿Por qué no añadir las notificaciones en el template?
        - Mantiene la lógica de preparación de datos en la vista (separación de responsabilidades).
        - Permite usar las notificaciones en múltiples partes del template sin repetir código.
        """
        context = super().get_context_data(**kwargs)
        #latest_notifications
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread()
        context['latest_notifications'] = latest_notifications[:3]
        context['number_of_notifications'] = latest_notifications.count()
        
        context['header_text'] = "Projects"
        return context