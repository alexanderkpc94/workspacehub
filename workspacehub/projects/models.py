"""
Modelos de la aplicación projects.

Define los modelos Project y Attachment para gestionar proyectos y sus archivos.
"""

from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from teams.models import Team
from .extra import STATUS_CHOICES, PRIORITY_CHOICES
from datetime import datetime


# Create your models here.


class ProjectQuerySet(models.QuerySet):
    """
    QuerySet personalizado para el modelo Project.
    
    Proporciona métodos de filtro reutilizables para consultas comunes.
    """
    
    def active(self):
        """Retorna solo proyectos activos (no archivados)."""
        return self.filter(active=True)
    
    def upcoming(self):
        """Retorna proyectos con fecha de vencimiento en el futuro."""
        return self.filter(due_date__gt=timezone.now())
    
    def due_soon(self):
        """
        Retorna proyectos que vencen pronto (dentro de 2 días).
        
        Combina los filtros active() y upcoming() para obtener solo
        proyectos activos que vencen pronto.
        """
        today = timezone.now().date()
        soon_threshold = today + timezone.timedelta(days=2)
        return self.active().upcoming().filter(due_date__lte=soon_threshold)


class ProjectManager(models.Manager):
    """
    Manager personalizado para el modelo Project.
    
    Encapsula la lógica del QuerySet y proporciona una API limpia.
    """
    
    def get_queryset(self):
        """Retorna el QuerySet personalizado."""
        return ProjectQuerySet(self.model, using=self._db)
    
    def all(self):
        """
        Sobrescritura de all() para aplicar filtros por defecto.
        
        Por defecto solo mostraremos proyectos activos y upcoming.
        """
        return self.get_queryset().active().upcoming()
    
    def due_soon(self):
        """Retorna proyectos que vencen dentro de 2 días."""
        return self.get_queryset().active().upcoming().due_soon()


class Project(models.Model):
    """
    Modelo principal que representa un proyecto.
    
    Un proyecto contiene tareas y pertenece a un equipo.
    Tiene información de seguimiento como presupuesto, duración estimada, etc.
    
    Campos principales:
    - owner: Usuario que creó el proyecto
    - team: Equipo al que pertenece el proyecto
    - status/priority: Estado y prioridad del proyecto
    - dates: Fechas de inicio y vencimiento
    - budget: Información financiera del proyecto
    """
    
    # El propietario del proyecto - puede ser diferente del líder del equipo
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    
    # UUID como clave primaria - más seguro que IDs secuenciales en URLs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # El equipo asociado al proyecto - importante para permisos y notificaciones
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    
    # Cliente/empresa para la que se realiza el proyecto
    client_company = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    
    #budget details
    # DecimalField para dinero - max_digits=12 permite hasta mil millones
    # decimal_places=2 permite centavos (ej: 1,234,567.89)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    amount_spent = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    
    # Duración estimada en días - help_text muestra una ayuda en el admin/formularios
    estimated_duration = models.IntegerField(blank=True, null=True, help_text="Estimated duration in days")
    
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    
    # Soft delete - permite archivar sin borrar
    active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    objects = ProjectManager()
   
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        
    def days_until_due(self):
        """Calcula días restantes hasta el vencimiento."""
        if self.due_date:
            current_date = timezone.now().date()
            return (self.due_date - current_date).days
        return None
    
    @property
    def progress_percentage(self):
        """Calcula el porcentaje de progreso según el estado."""
        progress_dict = {
            'To Do': 0,
            'In Progress': 50,
            'Completed': 100,
        }
        return progress_dict.get(self.status, 0)
    
    @property
    def status_color(self):
        """Retorna clase CSS para el color según el estado."""
        if self.progress_percentage == 100:
            return 'success'  # Green
        elif self.progress_percentage == 50:
            return 'warning'  # Yellow
        else:
            return ""  # Blue

    def priority_color(self):
        """Retorna código de color hexadecimal para la prioridad."""
        if self.priority == 'High':
            return '#e34d56'
        elif self.priority == 'Medium':
            return '#f2c745'
        else:
            return '#72e7a3'
        

#project file location
def project_attachment_path_location(instance, filename):
    """
    Define la ruta donde se guardarán los archivos adjuntos al proyecto.
    
    Estructura: attachments/{nombre_proyecto}/{fecha}/{nombre_archivo}
    """
    # get todays date YYYY-MM-DD format
    today_date = datetime.now().strftime('%Y-%m-%d')
    #return the upload path
    return "attachments/%s/%s/%s" % (instance.project.name, today_date, filename)
   

class Attachment(models.Model):
    """
    Modelo para almacenar archivos adjuntos a un proyecto.
    
    Permite a los usuarios subir documentos, imágenes, etc. relacionados con el proyecto.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=project_attachment_path_location)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment by {self.user.username} on {self.project.name}"