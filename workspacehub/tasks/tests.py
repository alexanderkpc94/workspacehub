"""
Tests para la aplicación tasks usando Django Test Client.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from projects.models import Project
from projects.forms import ProjectForm
from teams.models import Team


class ProjectListTestCase(TestCase):
    """Test para verificar lista y creación de proyectos."""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='gentech',
            email='test@example.com',
            password='1234'
        )
        
        self.team = Team.objects.create(
            name='Test Team',
            team_lead=self.user,
            created_by=self.user
        )
        self.team.members.add(self.user)
        
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            owner=self.user,
            team=self.team,
            status='To Do'
        )
        
        self.client.login(username='gentech', password='1234')
    
    def test_list_projects(self):
        """Verifica que la lista de proyectos responde correctamente."""
        response = self.client.get('/projects/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_create_project(self):
        """Verifica que se puede crear un proyecto."""
        response = self.client.post('/projects/create/', {
            'name': 'Nuevo Proyecto',
            'description': 'Descripción del proyecto',
            'priority': 'Medium',
            'team': self.team.id,
            'status': 'To Do',
        })
        self.assertIn(response.status_code, [200, 302])
        
        # Verifica que el proyecto fue creado en la base de datos
        project = Project.objects.filter(name='Nuevo Proyecto').first()
        self.assertIsNotNone(project)
