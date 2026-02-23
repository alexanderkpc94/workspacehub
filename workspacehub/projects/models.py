from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from teams.models import Team
from .extra import STATUS_CHOICES, PRIORITY_CHOICES
# Create your models here.


class ProjectQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)
    def upcoming(self):
        return self.filter(due_date__gt=timezone.now())
    def due_soon(self):
        today = timezone.now().date()
        soon_threshold = today + timezone.timedelta(days=2)
        return self.active().upcoming().filter(due_date__lte=soon_threshold)
class ProjectManager(models.Manager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)
    def all(self):
        return self.get_queryset().active().upcoming()
    def due_soon(self):
        return self.get_queryset().active().upcoming().due_soon()

class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    client_company = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    #budget details
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    amount_spent = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    estimated_duration = models.IntegerField(blank=True, null=True, help_text="Estimated duration in days")
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    objects = ProjectManager()
   
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