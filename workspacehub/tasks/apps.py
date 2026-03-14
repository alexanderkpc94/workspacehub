"""
Configuración de la aplicación tasks.
"""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    Configuración de la aplicación de tareas.
    
    default_auto_field especifica el tipo de campo para las claves primarias
    automáticas que Django añade a algunos modelos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
