from django.contrib import admin

# Register your models here.
from .models import Project, Attachment
from notifications.task import create_notification
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'team', 'status', 'priority', 'start_date', 'due_date')
     
    def save_model(self, request, obj, form, change):
        if not change:  # Only set the owner when creating a new project
            obj.owner = request.user
            message = f'New project, {obj.name} has been created.'
        else:
            message = f'Project updated, {obj.name}.'
        super().save_model(request, obj, form, change)    #saving project
        
        actor_username = request.user.username
        object_id = obj.id # Ensure ID is string for serialization
        create_notification.delay(actor_username, message, object_id)

admin.site.register(Project)
admin.site.register(Attachment)