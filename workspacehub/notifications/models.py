from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.

class NotificationManager(models.Manager):
    # def for_user(self, user):
    #     return self.filter(recipient=user).order_by('-created_at')
    def unread(self):
        return self.filter(read=False)
    def read(self):
        return self.filter(read=True)

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    message = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    objects = NotificationManager()

    def __str__(self):
        return f"{self.sender} {self.message} {self.content_object}"
    
    class Meta:
        ordering = ['-created_at']
        
    @property
    def notification_time_formatted(self):
        return self.created_at.strftime("%d %b %I:%M %p")
    
    @property
    def icon_class(self):
        model_name = self.content_type.model if self.content_type else None

        icons = {
            "project": "fas fa-comment bg-primary",
            # "post": "fas fa-camera bg-purple",
            "profile": "fas fa-user bg-info",
        }

        return icons.get(model_name, "fas fa-bell bg-secondary")
    
    @property
    def tipo_contenido(self):
        model_name = self.content_type.model if self.content_type else None

        icons = {
            "project": " actualizó un proyecto",
            # "post": "fas fa-camera bg-purple",
            "profile": " ha sido agregado",
        }

        return icons.get(model_name, " ha generado una nueva notificacion")
    
    def mark_as_read(self):
        self.read = True
        self.save(update_fields=["read"])
    