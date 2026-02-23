from celery import shared_task
from .models import Notification
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from projects.models import Project
@shared_task
def create_notification(actor_username, recipient_name, message, content_type_id, object_id):
    try:
        actor = User.objects.get(username=actor_username)
        recipient = User.objects.get(username=recipient_name)
        content_type = ContentType.objects.get(id=content_type_id)
        content_object = content_type.get_object_for_this_type(id=object_id)
        notification = Notification.objects.create(
            recipient=recipient,
            sender=actor,
            message=message,
            content_type=content_type,
            content_object=content_object,
            read=False,
        )
        return notification.message
        
    except User.DoesNotExist:
        return None
    except ContentType.DoesNotExist:
        return None
    
@shared_task
def notify_teams_due_projects_tasks():
    project_due_soon = Project.objects.due_soon()
    
    for project in project_due_soon:
        message = f'Reminder: The project {project.name} is due soon!'
        actor = project.owner.username
        content_type = ContentType.objects.get_for_model(Project)
        
        menbers = project.team.members.all()
        for member in menbers:
            create_notification.delay(actor_username=actor, recipient_name=member.username,
                message=message,
                content_type_id=content_type.id, object_id=project.id )