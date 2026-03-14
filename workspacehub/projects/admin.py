"""
Configuración del admin de Django para la aplicación projects.

Personaliza cómo se muestran los modelos en la interfaz de admin.
"""

from django.contrib import admin

# Register your models here.
from .models import Project, Attachment
# Importamos la tarea de notificaciones para enviar cuando se guarda un proyecto
from notifications.task import create_notification


class ProjectAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del admin para el modelo Project.
    
    ModelAdmin permite personalizar casi todo sobre cómo se muestra el modelo en el admin:
    - list_display: campos que se muestran en la lista
    - search_fields: campos searchable
    - list_filter: filtros laterales
    - etc.
    """
    
    # Muestra estas columnas en la lista de proyectos
    list_display = ('name', 'owner', 'team', 'status', 'priority', 'start_date', 'due_date')
     

    def save_model(self, request, obj, form, change):
        """
        Sobrescribe el método de guardado para enviar notificaciones.
        
        ¿Por qué sobrescribir save_model en lugar de usar signals?
        - Es más explícito: la lógica de notificaciones está aquí, no en otro lugar.
        - Permite diferenciar entre creación (change=False) y edición (change=True).
        - Menos acoplamiento que los signals.
        
        Args:
            request: La solicitud HTTP (contiene el usuario actual)
            obj: El objeto Project que se está guardando
            form: El formulario que se usó para guardar
            change: Boolean - True si es edición, False si es creación
        """
        if not change:  # Only set the owner when creating a new project
            obj.owner = request.user
            message = f'New project, {obj.name} has been created.'
        else:
            message = f'Project updated, {obj.name}.'
        super().save_model(request, obj, form, change)    #saving project
        
        # Preparar datos para la notificación
        actor_username = request.user.username
        object_id = obj.id # Ensure ID is string for serialization
        
        # .delay() encola la tarea para ejecutarse asíncronamente
        # No bloquea la respuesta del admin mientras envía la notificación
        create_notification.delay(actor_username, message, object_id)


# Registrar los modelos con sus configuraciones personalizadas
admin.site.register(Project)
admin.site.register(Attachment)