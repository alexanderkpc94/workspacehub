"""
Configuración de URLs de la aplicación projects.

Define las rutas para gestión de proyectos y el tablero Kanban.
"""

from django.urls import path
from .views import (ProjectCreateView, 
                    ProjectListView, ProjectNearDueListView, ProjectDetailView, KanbanBoardView)


app_name = 'projects'

urlpatterns = [
    # Lista de proyectos - página principal de proyectos
    path('', ProjectListView.as_view(), name='list'),
    
    # Proyectos próximos a vencer
    path('near-due-list', ProjectNearDueListView.as_view(), name='due-list'),
    
    # Crear nuevo proyecto
    path('create/', ProjectCreateView.as_view(), name='create'),
    
    # Ver detalle de un proyecto específico (UUID como identificador)
    path('<uuid:pk>', ProjectDetailView.as_view(), name='project-detail'),
    
    # Tablero Kanban del proyecto
    path('<uuid:pk>/kanban-board', KanbanBoardView.as_view(), name='kanban-board'),
]
