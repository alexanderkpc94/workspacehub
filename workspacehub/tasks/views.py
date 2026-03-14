"""
Vistas de la aplicación tasks.

Contiene las funciones para gestionar tareas vía AJAX y formularios:
- Actualizar estado de tarea (arrastrar en kanban)
- Crear tareas (vía formulario y AJAX)
- Obtener detalles de tarea
- Actualizar tarea
"""

from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
import json
from django.http import JsonResponse
from .models import Task
from projects.models import Project
from .forms import TaskAddForm
from django.contrib import messages
from django.shortcuts import redirect
from .forms import TaskUpdateForm
# from notifications.tasks import create_notification


@require_POST
def update_task_status_ajax(request, task_id):
    """
    Actualiza el estado de una tarea vía AJAX.
    
    ¿Por qué usar AJAX aquí?
    - El kanban permite arrastrar tareas entre columnas sin recargar la página.
    - AJAX proporciona una experiencia de usuario más fluida e interactiva.
    - reduce la carga del servidor al transferir solo datos (no HTML completo).
    
    Flujo:
    1. Recibe JSON con el nuevo estado
    2. Valida que el estado sea válido
    3. Actualiza la tarea en la base de datos
    4. Retorna success/error como JSON
    
    @require_POST: Decorador que seguridad - solo acepta método POST.
    """
    try:
        task = Task.objects.get(id=task_id)
        # request.body contiene el cuerpo raw de la solicitud
        # json.loads() convierte el string JSON a diccionario Python
        data = json.loads(request.body)

        # Obtenemos el nuevo estado del JSON y capitalizamos (Backlog -> Backlog)
        # .title() pone en mayúscula la primera letra de cada palabra
        new_status = data.get('status').title()
        print(new_status)

        # check if status is valid
        # Validación del lado del servidor - nunca confíes en el cliente
        if new_status in ['Backlog', 'To Do', 'In Progress', 'Completed']:
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
    

@require_POST
def create_task(request):
    """
    Crea una nueva tarea desde el formulario del kanban.
    
    ¿Por qué usar @require_POST?
    - Solo acepta solicitudes POST (no GET).
    - POST es el método apropiado para crear recursos (según REST).
    - Protege contra ataques CSRF (Django lo maneja automáticamente).
    
    Diferencia con create_task_ajax:
    - Esta versión usa formularios Django tradicionales (con validación de formularios).
    - Más robusta para casos donde el usuario necesita llenar muchos campos.
    - Retorna una respuesta HTTP redirect después de crear.
    """
    
    project_id = request.POST.get('project_id')
    
    # Validación: si no hay proyecto, no podemos crear la tarea
    if not project_id:
        messages.error(request, "Project ID is required.")
        return redirect('projects:kanban-board', pk=project_id)  
    
    # TaskAddForm valida los datos del formulario según las reglas definidas en forms.py
    task_form = TaskAddForm(request.POST)
    if task_form.is_valid():
        status = request.POST.get('status').title()
        try:
            # Obtenemos el proyecto para asociar la tarea
            project = Project.objects.get(id=project_id)
            
            # Guardamos la tarea pero sin commit (commit=False) para poder añadir campos adicionales
            task = task_form.save(commit=False)
            task.project = project
            task.owner = request.user  # El usuario actual que está logueado
            
            # Validamos el estado antes de asignar
            if status in ['Backlog', 'To Do', 'In Progress', 'Completed']:
                task.status = status
            task.save()
            messages.success(request, "Tarea creada.")
            return redirect('projects:kanban-board', pk=project.id)
        except:
            return redirect('projects:kanban-board', pk=project.id)
    else:
        messages.error(request, "Error creating the new task, invalid form")
    return redirect('projects:kanban-board', pk=project_id)


@require_POST
def create_task_ajax(request):
    """
    Crea una tarea de forma rápida vía AJAX (para el botón "rápido" del kanban).
    
    ¿Por qué tener dos métodos de crear tarea?
    - Este es para creación rápida: solo nombre y proyecto.
    - create_task() es para creación completa con todos los campos.
    - Permite UX diferentes: una输入 mínima vs. formulario completo.
    
    Retorna JSON en lugar de redirect - la UI puede decidir qué hacer.
    """
    name = request.POST.get('name')
    project_id = request.POST.get('project_id')
    user = request.user

    # Validación básica - el nombre es obligatorio
    if not name:
        return JsonResponse({'success': False, 'error': 'Task title is required'})
    
    if not project_id:
        return JsonResponse({'success': False, 'error': 'Project ID is required'})
    
    try:
        project = Project.objects.get(id=project_id)

        # create new task
        # Create() es un atajo que crea y guarda en una sola operación
        new_task = Task.objects.create(name=name, project=project, owner=user)

        return JsonResponse({'success': True, 'task_id': new_task.id})
    except Project.DoesNotExist:
         return JsonResponse({'success': False, 'error': 'Project not found'})
    

def get_task(request, task_id):
    """
    Obtiene los detalles de una tarea específica vía AJAX.
    
    ¿Por qué retornar JSON en lugar de renderizar HTML?
    - El frontend puede decidir cómo mostrar los datos (modal, sidebar, etc.).
    - Reduce el acoplamiento entre backend y presentación.
    - Más flexible para aplicaciones de una sola página (SPA).
    """
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': "Task not found"},  status=400)
    
    if request.method == "GET":
        # Preparamos un diccionario con los datos de la tarea
        # .isoformat() convierte la fecha a string en formato ISO 8601
        task_data = {
            "task_id": str(task.id),
            "name": task.name,
            "description": task.description,
            "start_date": task.start_date.isoformat() if task.start_date else "",
            "due_date": task.due_date.isoformat() if task.due_date else "",
            "priority": task.priority
        }
        return JsonResponse({"task_data": task_data})
        

def update_task(request, task_id):
    """
    Actualiza una tarea existente vía AJAX.
    
    Usa get_object_or_404() para manejar el caso donde la tarea no existe:
    - Si existe: retorna la tarea
    - Si no existe: retorna automáticamente un 404 (más limpio que hacer try/except manual)
    """
    try:
        task = get_object_or_404(Task, id=task_id)
        if request.method == "POST":
            # instance=task indica que queremos actualizar esa tarea específica
            # prefix='edit' evita conflictos de IDs si hay múltiples formularios en la página
            form = TaskUpdateForm(request.POST, instance=task, prefix='edit')
            if form.is_valid():
                form.save()
                # Retornamos los datos actualizados para que el frontend pueda actualizar la UI
                return JsonResponse({'success': True,  'updatedTask':  {
                    "id": str(task.id),
                    "name": task.name,
                    "description": task.description,
                    "start_date": task.start_date.isoformat() if task.start_date else "",
                    "due_date": task.due_date.isoformat() if task.due_date else "",
         }})
            else:
                # Retornamos los errores de validación para que el frontend los muestre
                return JsonResponse({'success': False, 'errors': form.errors})
        
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)