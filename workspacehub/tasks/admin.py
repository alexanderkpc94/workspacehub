"""
Configuración del admin de Django para la aplicación tasks.

Permite a los administradores gestionar tareas desde la interfaz de admin.
"""

from django.contrib import admin
from .models import Task
# Register your models here.
# Al registrar Task en el admin, los administradores pueden:
# - Ver todas las tareas con su estado, prioridad, proyecto, etc.
# - Filtrar por proyecto, estado, prioridad
# - Buscar por nombre
# - Editar o crear tareas desde el admin
admin.site.register(Task)