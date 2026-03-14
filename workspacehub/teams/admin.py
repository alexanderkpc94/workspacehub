"""
Configuración del admin de Django para la aplicación teams.

Permite gestionar equipos desde la interfaz administrativa.
"""

from django.contrib import admin
from .models import Team
# Register your models here.
# Al registrar Team en el admin, los administradores pueden:
# - Ver lista de equipos
# - Crear/editar equipos
# - Asignar líderes y miembros
# - Filtrar por líder, fecha de creación
admin.site.register(Team)