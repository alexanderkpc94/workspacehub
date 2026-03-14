"""
Formularios de la aplicación projects.

Contiene los formularios para crear proyectos y adjuntos.
"""

from django import forms
from .models import Project, Attachment
# Widget de fecha moderno - más atractivo que el input nativo
from tempus_dominus.widgets import DatePicker
# from django.contrib.auth.models import User
from teams.models import Team
# Las choices se importan desde extra.py para mantener consistencia
from .extra import STATUS_CHOICES, PRIORITY_CHOICES


class ProjectForm(forms.ModelForm):
    """
    Formulario para crear y editar proyectos.
    
    Cada campo se personaliza con widgets y atributos para mejorar la UX:
    - placeholders: textos de ayuda dentro de los campos
    - label=False: oculta las etiquetas (el diseño ya las incluye)
    - attrs: clases CSS para estilos
    """
    
    # TextInput con placeholder - campo de texto con sugerencia
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter project name...'}), label=False, required=True)
    
    # Textarea para descripción larga
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter project description...'}), label=False, required=True)
    
    # DatePicker - widget de calendario moderno
    start_date = forms.DateTimeField(widget=DatePicker(attrs={'append': 'fa fa-calendar', 'icon_toggle': True}), label=False, required=False)
    due_date = forms.DateTimeField(widget=DatePicker(attrs={'append': 'fa fa-calendar', 'icon_toggle': True}), label=False, required=False)
    
    # owner = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    
    # CharField simple para el nombre del cliente
    client_company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter client company name...'}), label=False, required=False)
    
    # ChoiceField con widget Select - genera dropdowns
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    
    # ModelChoiceField - dropdown que carga opciones desde la base de datos
    team = forms.ModelChoiceField(queryset=Team.objects.all(), widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class':"form-control"}), label=False, required=True)
    
    # DecimalField para valores monetarios - NumberInput es más apropiado que TextInput
    total_amount = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Enter total budget amount...'}), label=False, required=False)
    amount_spent = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Enter amount spent...'}), label=False, required=False)
    
    # IntegerField para duración en días
    estimated_duration = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Enter estimated duration in days...'}), label=False, required=False)
    
    
    class Meta:
        model = Project
        # Campos que se incluirán en el formulario
        fields = ['name', 'team','description', 'status', 'client_company', 'priority',  'start_date', 'due_date', 'total_amount', 'amount_spent', 'estimated_duration']
        

class AttachmentForm(forms.ModelForm):
    """
    Formulario para subir archivos a un proyecto.
    
    Muy simple: solo un campo de archivo.
    El modelo Attachment se encarga de relacionar el archivo con el proyecto.
    """
    
    class Meta:
        model= Attachment
        fields = ['file']
        