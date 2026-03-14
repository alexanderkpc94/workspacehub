"""
Modelos de la aplicación teams.

Define el modelo Team para gestionar equipos de trabajo.
"""

from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Team(models.Model):
    """
    Modelo que representa un equipo de trabajo.
    
    Los equipos son la forma de organizar a los usuarios y asociarlos con proyectos.
    Cada proyecto pertenece a un equipo, y los miembros del equipo pueden acceder a él.
    
    Relaciones:
    - team_lead: Usuario que lidera el equipo
    - members: Usuarios que pertenecen al equipo (ManyToMany)
    - created_by: Usuario que creó el equipo
    """
    
    # Nombre único del equipo
    name = models.CharField(max_length=255 , unique=True)
    
    # Descripción opcional del equipo
    description = models.TextField(null=True, blank=True)
    
    # Líder del equipo - puede ser diferente del creador
    # related_name='led_team' permite: user.led_team para obtener equipos que lidera
    team_lead = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_team')
    
    # Miembros del equipo - relación muchos a muchos
    # Un usuario puede pertenecer a múltiples equipos
    # Un equipo puede tener múltiples usuarios
    # related_name='teams' permite: user.teams.all() para obtener equipos del usuario
    members = models.ManyToManyField(User, related_name='teams')
    
    # Usuario que creó el equipo (puede ser diferente del líder)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    
    # Fecha de creación automática
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Representación en string del equipo."""
        return self.name
    
    