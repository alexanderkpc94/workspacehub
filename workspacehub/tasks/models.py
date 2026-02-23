from django.utils import timezone
from django.db import models
from projects.models import Project
from django.contrib.auth.models import User
import uuid
# Create your models here.
STATUS_CHOICES = [
    ('To Do', 'To Do'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
]

PRIORITY_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
]

class TaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)
    def upcoming(self):
        return self.filter(due_date__gt=timezone.now())

class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)
    def all(self):
        return self.get_queryset().active().upcoming()


class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    objects = TaskManager()
   
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        
    def days_until_due(self):
        if self.due_date:
            #get the current date
            current_date = timezone.now().date()
            return (self.due_date - current_date).days
        return None
    
    @property
    def progress_percentage(self):
        progress_dict = {
            'To Do': 0,
            'In Progress': 50,
            'Completed': 100,
        }
        return progress_dict.get(self.status, 0)
    
    @property
    def status_color(self):
        if self.progress_percentage == 100:
            return 'success'  # Green
        elif self.progress_percentage == 50:
            return 'warning'  # Yellow
        else:
            return ""  # Blue

    def priority_color(self):
        if self.priority == 'High':
            return '#e34d56'
        elif self.priority == 'Medium':
            return '#f2c745'
        else:
            return '#72e7a3'