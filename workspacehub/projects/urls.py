from django.urls import path
from .views import ProjectCreateView, ProjectListView

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='list'),
    path('create/', ProjectCreateView.as_view(), name='create'),
]