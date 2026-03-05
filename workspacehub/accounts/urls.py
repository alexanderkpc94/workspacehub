from django.urls import path
from .views import DashboardView,MembersListView,RegisterView

app_name = 'accounts'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('members', MembersListView.as_view(), name='member-list'),
    path('register/', RegisterView, name='register'),
]
