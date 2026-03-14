"""
Módulo de modelos de la aplicación accounts.

Este archivo define el modelo Profile, que extiende el modelo User de Django
para almacenar información adicional del usuario como foto de perfil, bio, etc.
"""

from datetime import datetime
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
#import django signals
# Los signals son mecanismo de Django para responder a eventos del ORM.
# post_save se dispara después de guardar un objeto en la base de datos.
# Se usa aquí para crear automáticamente un Profile cuando se crea un User.
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


def profile_image_path_location(instance, filename):
    """
    Función personalizada para determinar la ruta donde se guardarán las fotos de perfil.
    
    Por qué usamos una función así:
    -Organiza las imágenes por usuario y fecha, facilitando su gestión.
    -Evita conflictos de nombres si varios usuarios suben archivos con el mismo nombre.
    -La fecha en el path permite hacer limpieza periódica si es necesario.
    """
    # get todays date YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')
    #return the upload path
    return "profile_pictures/%s/%s/%s" % (instance.user.username, today, filename)


class Profile(models.Model):
    """
    Modelo que extiende la información del usuario.
    
    ¿Por qué no guardar todo en el modelo User?
    - El modelo User de Django es limitado por diseño (es genérico para cualquier proyecto).
    - Separar el perfil permite añadir campos específicos sin modificar la tabla auth_user.
    - Facilita la migración y actualización de Django (el modelo User puede cambiar entre versiones).
    - Permite tener una relación uno a uno con User (un usuario = un perfil).
    """
    
    # OneToOneField crea una relación 1:1 con User. on_delete=models.CASCADE significa
    # que si se elimina el usuario, también se elimina su perfil (cuidado: esto puede ser dangerous
    # en producción, a veces es mejor usar SET_NULL).
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # related_name='profile' permite acceder al perfil desde el usuario con user.profile
    
    # Información profesional
    job_title = models.CharField(max_length=255, blank=True, null=True)  # Título del puesto
    profile_picture = models.ImageField(upload_to=profile_image_path_location, blank=True, null=True)  # Foto de perfil
    bio = models.TextField(blank=True, null=True)  # Biografía/acerca de
    
    # Información de ubicación y contacto
    location = models.CharField(max_length=100, blank=True, null=True)  # Ciudad/país
    phone = PhoneNumberField(null=True, blank=True, unique=True)  # Teléfono con validación internacional
    birth_date = models.DateField(blank=True, null=True)  # Fecha de nacimiento
    
    joind_date = models.DateTimeField(auto_now_add=True)  # Fecha de registro (auto, no editable)

    def __str__(self):
        """Representación en string del perfil - útil en el admin de Django."""
        return self.user.username

    @property
    def profile_picture_url(self):
        """
        Property (propiedad) que retorna la URL de la foto de perfil.
        
        ¿Por qué usar una property en lugar de un campo?
        - Proporciona un valor por defecto si no hay imagen (evita errores en templates).
        - Permite lógica adicional (como procesar la imagen, generar thumbnails, etc.).
        - Se accede como atributo (obj.foto) no como método (obj.foto()).
        """
        try:
            image = self.profile_picture.url
        except:
            # Si no hay imagen o hay error, retornamos una imagen por defecto
            image = '/static/dist/img/default-150x150.png'
        return image

    @property
    def full_name(self):
        """
        Retorna el nombre completo del usuario.
        
        ¿Por qué no usar user.get_full_name()?
        - Permite personalizar el formato (aquí usa username como fallback).
        - El campo first_name y last_name son opcionales en Django User.
        - Gives una experiencia más consistente mostrando el username si no hay nombre.
        """
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username 


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, **kwargs):
    """
    Signal de Django que se dispara cada vez que se guarda un objeto User.
    
    ¿Por qué usamos un signal aquí?
    - Garantiza que cada usuario tenga un Profile asociado desde su creación.
    - Evita inconsistencias si alguien crea un usuario por código sin crear el perfil.
    - get_or_create() es seguro: crea solo si no existe, o retorna el existente.
    
    Args:
        sender: El modelo que dispatch el signal (User)
        instance: La instancia específica del usuario que se guardó
        **kwargs: Argumentos adicionales del signal
    """
    Profile.objects.get_or_create(user=instance)