"""
Configuración de la aplicación accounts.

Este archivo define la configuración de la app para Django.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Clase de configuración para la aplicación accounts.
    
    ¿Por qué necesitamos AppConfig?
    - Define metadatos de la aplicación (nombre, etc.).
    - default_auto_field especifica qué tipo de campo usar para las PK automáticamente.
    - BigAutoField es el tipo por defecto y funciona bien para la mayoría de casos.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
