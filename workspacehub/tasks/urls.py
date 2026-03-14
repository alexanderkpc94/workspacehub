"""
Configuración de URLs de la aplicación tasks.

Define las rutas para las operaciones CRUD de tareas.
"""

from django.urls import path
from .views import (
    update_task_status_ajax, 
    create_task,
    create_task_ajax,
    get_task,
    update_task, 
    # assign_user_to_task, 
    # get_task_assignment_form
    )

app_name = 'tasks'

urlpatterns = [
    # Actualizar estado de tarea - usa UUID como identificador
    # <uuid:task_id> captura el UUID de la URL y lo pasa como argumento a la vista
    path('update-task-status-ajax/<uuid:task_id>/', update_task_status_ajax, name="update-task-status"),
    
    # Crear tarea (formulario tradicional)
    path('create-task/', create_task, name="create-task"),
    
    # Crear tarea (vía AJAX - más ligero)
    path('create-task-ajax/', create_task_ajax, name="create-task-ajax"),
    
    # Obtener detalles de una tarea
    path('<uuid:task_id>/get/', get_task, name='get_task'),
    
    # Actualizar una tarea existente
    path('<uuid:task_id>/update/', update_task, name='update_task')
]