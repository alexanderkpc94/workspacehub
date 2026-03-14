"""
Configuración del admin de Django para la aplicación accounts.

El admin de Django es una interfaz administrativa automática muy poderosa.
Permite gestionar los modelos desde una interfaz web sin escribir código adicional.
"""

from django.contrib import admin
from .models import Profile


# Register your models here.
# Al registrar Profile en el admin, los administradores pueden:
# - Ver lista de todos los perfiles
# - Crear/editar/borrar perfiles
# - Filtrar y buscar por campos
# - Personalizar qué campos son editables, etc.
admin.site.register(Profile)