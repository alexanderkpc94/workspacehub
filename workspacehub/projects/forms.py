from django import forms
from .models import Project
from tempus_dominus.widgets import DatePicker
# from django.contrib.auth.models import User
from teams.models import Team
from .extra import STATUS_CHOICES, PRIORITY_CHOICES
class ProjectForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter project name...'}), label=False, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter project description...'}), label=False, required=True)
    start_date = forms.DateTimeField(widget=DatePicker(attrs={'append': 'fa fa-calendar', 'icon_toggle': True}), label=False, required=False)
    due_date = forms.DateTimeField(widget=DatePicker(attrs={'append': 'fa fa-calendar', 'icon_toggle': True}), label=False, required=False)
    # owner  = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    client_company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter client company name...'}), label=False, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    team = forms.ModelChoiceField(queryset=Team.objects.all(), widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    total_amount = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Enter total budget amount...'}), label=False, required=False)
    amount_spent = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Enter amount spent...'}), label=False, required=False)
    estimated_duration = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Enter estimated duration in days...'}), label=False, required=False)
    
    
    class Meta:
        model = Project
        fields = ['name', 'team','description', 'status', 'client_company', 'priority',  'start_date', 'due_date', 'total_amount', 'amount_spent', 'estimated_duration']