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
# from notifications.tasks import create_notification


@require_POST
def update_task_status_ajax(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        data = json.loads(request.body)

        new_status = data.get('status').title()
        print(new_status)

        # check if status is valid
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
    
    project_id = request.POST.get('project_id')
    
    if not project_id:
        messages.error(request, "Project ID is required.")
        return redirect('projects:kanban-board', pk=project.id)  
    
    task_form = TaskAddForm(request.POST)
    if task_form.is_valid():
        status = request.POST.get('status').title()
        try:
            project = Project.objects.get(id=project_id)
            task = task_form.save(commit=False)
            task.project = project
            task.owner = request.user
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
    name = request.POST.get('name')
    project_id = request.POST.get('project_id')
    user = request.user

    if not name:
        return JsonResponse({'success': False, 'error': 'Task title is required'})
    
    if not project_id:
        return JsonResponse({'success': False, 'error': 'Project ID is required'})
    
    try:
        project = Project.objects.get(id=project_id)

        # create new task
        new_task = Task.objects.create(name=name, project=project, owner=user)

        return JsonResponse({'success': True, 'task_id': new_task.id})
    except Project.DoesNotExist:
         return JsonResponse({'success': False, 'error': 'Project not found'})