"""
Constantes compartidas de la aplicación projects.

Este archivo contiene opciones (choices) que se usan en múltiples lugares
para mantener consistencia en toda la aplicación.
"""

# Opciones de estado para proyectos y tareas en el sistema Kanban
# ¿Por qué no usar enumeraciones (Enum)?
# - Django tiene su propio sistema de choices que se integra mejor con formularios y admin.
# - Son más fáciles de modificar sin cambiar código en varios lugares.
# - El primer valor es el que se guarda en la BD, el segundo es el label mostrado al usuario.
STATUS_CHOICES = [
    ('To Do', 'To Do'),          # Por hacer - tareas/proyectos pendientes de iniciar
    ('In Progress', 'In Progress'),  # En progreso - actualmente trabajándose
    ('Completed', 'Completed'),   # Completado - terminado
]

# Opciones de prioridad para proyectos y tareas
# Usado para ordenar y filtrar por importancia
PRIORITY_CHOICES = [
    ('Low', 'Low'),       # Baja prioridad - puede esperar
    ('Medium', 'Medium'), # Prioridad media - estándar
    ('High', 'High'),    # Alta prioridad - requiere atención inmediata
]
