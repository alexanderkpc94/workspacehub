"""
Modelos de la aplicación tasks.

Define el modelo Task para gestionar las tareas del proyecto con sistema Kanban.
"""

from django.utils import timezone
from django.db import models
from projects.models import Project
from django.contrib.auth.models import User
import uuid

# Create your models here.

# STATUS_CHOICES define las opciones posibles para el estado de una tarea en el kanban.
# ¿Por qué no usar un simple CharField?
# - choices强制限制 los valores possíveis (evita errores de spelling).
# - Genera automáticamente un dropdown en formularios y admin.
# - Mantiene consistencia en toda la aplicación.
STATUS_CHOICES = [
    ('Backlog', 'Backlog'),      # Tareas pendientes de planificar
    ('To Do', 'To Do'),          # Tareas listas para hacer
    ('In Progress', 'In Progress'),  # Tareas en curso
    ('Completed', 'Completed'),   # Tareas terminadas
]

# PRIORITY_CHOICES similar al anterior, define niveles de prioridad
PRIORITY_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
]


class TaskQuerySet(models.QuerySet):
    """
    QuerySet personalizado para el modelo Task.
    
    ¿Qué es un QuerySet?
    - Es una representación de una consulta a la base de datos.
    - Permite encadenar filtros de forma fluida (Task.objects.active().upcoming()).
    - Los QuerySets personalizados definen métodos reutilizables.
    
    ¿Por qué separar la lógica en QuerySet en lugar de Managers?
    - QuerySets permiten encadenamiento: Task.objects.active().upcoming()
    - Managers son el punto de entrada: Task.objects.all()
    - Esta arquitectura permite filtrar y luego encadenar más filtros.
    """
    
    def active(self):
        """Retorna solo tareas activas (no archivadas/eliminadas lógicamente)."""
        return self.filter(active=True)
    
    def upcoming(self):
        """
        Retorna tareas que vencen en el futuro o no tienen fecha de vencimiento.
        
        ¿Por qué incluir las sin fecha?
        - Las tareas sin fecha límite no deberían filtrarse, siempre son "próximas".
        - Evita que desaparezcan de vistas de "tareas pendientes".
        """
        return self.filter(
            models.Q(due_date__gte=timezone.now()) | models.Q(due_date__isnull=True))


class TaskManager(models.Manager):
    """
    Manager personalizado para el modelo Task.
    
    ¿Qué es un Manager?
    - Es la interfaz a través de la cual Django proporciona operaciones de base de datos.
    - Por defecto, cada modelo tiene objects = models.Manager()
    - Los Managers personalizados añaden métodos de utilidad.
    
    ¿Por qué usar Manager + QuerySet?
    - El Manager deleg al QuerySet para el trabajo pesado.
    - Permite Task.objects.all() llame internamente a los filtros de TaskQuerySet.
    - Mantiene la API limpia: Task.objects.all() retorna tareas actives y upcoming.
    """
    
    def get_queryset(self):
        """Retorna un QuerySet personalizado en lugar del estándar."""
        return TaskQuerySet(self.model, using=self._db)
    
    def all(self):
        """
        Sobrescritura de all() para aplicar filtros por defecto.
        
        ¿Por qué hacer esto?
        - Por defecto solo mostraremos tareas activas y upcoming.
        - Evita que el usuario vea tareas archivadas o vencidas accidentalmente.
        - El usuario puede usar .all() del QuerySet si necesita las vencidas.
        """
        return self.get_queryset().active().upcoming()


class Task(models.Model):
    """
    Modelo principal que representa una tarea en el sistema Kanban.
    
    Flujo typical:
    1. Se crea con status='Backlog' (por defecto)
    2. Se mueve a 'To Do' cuando está lista para trabajarse
    3. Se marca 'In Progress' cuando alguien la toma
    4. Se completa cuando está terminada
    
    Campos:
    - owner: Usuario que creó la tarea (responsable)
    - project: Proyecto al que pertenece la tarea (relación многие-a-uno)
    - status/priority: Controlan la visualización en el kanban
    - start_date/due_date: Fechas para planificación
    - active: Soft delete - permite archivar sin borrar de la DB
    """
    
    # ForeignKey a User - cada tarea pertenece a un usuario (el creador/responsable)
    # on_delete=models.CASCADE significa: si se borra el usuario, se borran sus tareas
    # related_name='task' permite: user.task.all() para obtener tareas del usuario
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task')
    
    # UUID como clave primaria en lugar de auto-increment.
    # ¿Por qué UUID?
    # - No revela la cantidad de objetos (más seguro en URLs públicas)
    # - Permite合并 bases de datos sin conflictos de IDs
    # - URLs más amigables: /tasks/550e8400-e29b-41d4-a716-446655440000/
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=250)  # Título de la tarea
    
    # ForeignKey al proyecto - cada tarea pertenece a un proyecto
    # related_name='tasks' permite: project.tasks.all() para obtener tareas del proyecto
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    
    # description puede estar vacía (blank=True) o ser nula (null=True)
    description = models.TextField(blank=True, null=True)
    
    # CharField con choices - limita los valores posibles a STATUS_CHOICES
    # default='Backlog' significa que las tareas nuevas start en backlog
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Backlog')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    
    # Fechas - pueden ser nulas (tarea sin fecha límite específica)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    
    # Soft delete: en lugar de borrar la tarea, la marcamos como inactiva
    active = models.BooleanField(default=True)
    
    # Timestamps automáticos
    created_at = models.DateTimeField(auto_now_add=True)  # Se setea solo al crear
    update_at = models.DateTimeField(auto_now=True)  # Se actualiza en cada save()
    
    # Asignamos nuestro manager personalizado
    objects = TaskManager()
   
    def __str__(self):
        """Representación en string - útil en el admin y debug."""
        return self.name

    class Meta:
        ordering = ['-created_at']  # Ordenar por más recientes primero
        
    def days_until_due(self):
        """
        Calcula cuántos días faltan para el vencimiento.
        
        Retorna:
        - int: número de días (positivo si falta, negativo si pasó)
        - None: si no hay fecha de vencimiento
        
        ¿Por qué un método en lugar de property?
        - Calculation requiere lógica (obtener fecha actual, restar).
        - Las properties son mejores para valores simples sin procesamiento.
        """
        if self.due_date:
            #get the current date
            current_date = timezone.now().date()
            return (self.due_date - current_date).days
        return None
    
    @property
    def progress_percentage(self):
        """
        Calcula el porcentaje de progreso según el estado de la tarea.
        
        ¿Por qué un property en lugar de campo en la base de datos?
        - El progreso depende exclusivamente del status (derivado, no almacenado).
        - Almacenar datos derivados puede causar inconsistencias.
        - Se calcula al vuelo, siempre sincronizado con el status.
        """
        progress_dict = {
            'To Do': 0,
            'In Progress': 50,
            'Completed': 100,
        }
        return progress_dict.get(self.status, 0)
    
    @property
    def status_color(self):
        """
        Retorna el color CSS associated con el estado para mostrar en la UI.
        
        Esta propiedad se usa en las plantillas para aplicar clases CSS:
        - success = verde (tarea completada)
        - warning = amarillo (en progreso)
        - vacío = azul (por hacer/backlog)
        """
        if self.progress_percentage == 100:
            return 'success'  # Green
        elif self.progress_percentage == 50:
            return 'warning'  # Yellow
        else:
            return ""  # Blue

    def priority_color(self):
        """
        Retorna el código de color hexadecimal para la prioridad.
        
        A diferencia de status_color (que retorna nombre de clase CSS),
        aquí retornamos colores específicos:
        - High: Rojo (#e34d56)
        - Medium: Amarillo (#f2c745)
        - Low: Verde (#72e7a3)
        
        ¿Por qué retornar colores en lugar de clases CSS?
        - Da más control sobre la implementación visual exact.
        - Puede ser útil para gráficos o elementos que no usan clases CSS.
        """
        if self.priority == 'High':
            return '#e34d56'
        elif self.priority == 'Medium':
            return '#f2c745'
        else:
            return '#72e7a3'