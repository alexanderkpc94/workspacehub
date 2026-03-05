from django.urls import path
from .views import (
    update_task_status_ajax, 
    create_task,
    create_task_ajax,
    # update_task, 
    # assign_user_to_task, 
    # get_task_assignment_form
    )

app_name = 'tasks'

urlpatterns = [
    path('update-task-status-ajax/<uuid:task_id>/', update_task_status_ajax, name="update-task-status"),
    path('create-task/', create_task, name="create-task"),
    path('create-task-ajax/', create_task_ajax, name="create-task-ajax"),
]