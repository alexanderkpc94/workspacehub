"""
Configuración de URLs de la aplicación accounts.

Define las rutas URL para el dashboard, lista de miembros y registro.
"""

from django.urls import path
from .views import DashboardView, MembersListView, RegisterView

app_name = 'accounts'

urlpatterns = [
    # '' (raíz) mapea al dashboard - es la página principal después del login
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Lista de todos los miembros/perfiles del sistema
    path('members', MembersListView.as_view(), name='member-list'),
    
    # Página de registro de nuevos usuarios
    path('register/', RegisterView, name='register'),
]
