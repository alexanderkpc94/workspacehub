"""
Configuración de la aplicación teams.
"""

from django.apps import AppConfig


class TeamsConfig(AppConfig):
    """
    Configuración de la aplicación de equipos.
    
    default_auto_field especifica el tipo de campo para las claves primarias
    automáticas que añade Django a algunos modelos.
    BigAutoField es el tipo por defecto y funciona bien para la mayoría de casos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teams'
