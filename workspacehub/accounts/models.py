from datetime import datetime
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
#import django signals
from django.db.models.signals import post_save
from django.dispatch import receiver

#profile picture location
def profile_image_path_location(instance,filename):
    # get todays date YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')
    #return the upload path
    return "profile_pictures/%s/%s/%s" % (instance.user.username,today,filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to=profile_image_path_location, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    joind_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.user.username
    @property
    def profile_picture_url(self):
        try:
            image = self.profile_picture.url
        except:
            image = '/static/dist/img/default-150x150.png'
        return image    # Return a default image URL if no profile picture is set
    @property
    def full_name(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username 
        
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)