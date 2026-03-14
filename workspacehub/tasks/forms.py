"""
Formularios de la aplicación tasks.

Contiene los formularios para crear y actualizar tareas.
"""

from django import forms
from django.contrib.auth.models import User
# tempus_dominus es un widget de fecha/hora moderno para Django
# Proporciona un calendario visual atractivo en lugar del input date nativo
from tempus_dominus.widgets import DatePicker
from .models import Task
# Importamos las choices desde projects/extra.py para mantener consistencia
# ¿Por qué no definir las choices aquí mismo?
# - DRY (Don't Repeat Yourself): si las defines en un solo lugar, solo hay un lugar que cambiar.
# - Garantiza que tasks y projects usen exactamente los mismos valores.
from projects.extra import STATUS_CHOICES, PRIORITY_CHOICES


class TaskUpdateForm(forms.ModelForm):
    """
    Formulario para actualizar una tarea existente.
    
    ¿Por qué heredar de ModelForm en lugar de Form?
    - ModelForm genera automáticamente los campos desde el modelo.
    - Maneja la validación de forma automática según los campos del modelo.
    - save() sabe qué hacer (actualizar vs crear).
    - Mucho menos código que escribir cada campo manualmente.
    
    El prefijo 'edit' en las vistas避免 conflictos si hay múltiples formularios.
    """
    
    # HiddenInput es un campo oculto - útil cuando necesitamos el ID de la tarea
    # pero no queremos que el usuario lo vea o lo modifique.
    task_id = forms.CharField(widget=forms.HiddenInput(), required=True)

    description = forms.CharField(
        # Textarea permite varias líneas de texto
        widget= forms.Textarea(
            attrs={'rows': 3, 'placeholder': 'Describe your task here ...'}
        ),
        required=False  # La descripción es opcional
    )

    # DateTimeField con DatePicker - widget de calendario moderno
    # tempus_dominus proporciona mejor UX que el input date nativo del navegador
    start_date = forms.DateTimeField(
        widget=DatePicker(
            attrs= {
                'append': 'fa fa-calendar',  # Icono de calendario
                'icon_toggle': True  # Permite abrir el calendario haciendo click en el icono
            }
        )
    )

    due_date = forms.DateTimeField(
        widget=DatePicker(
            attrs= {
                'append': 'fa fa-calendar',
                'icon_toggle': True
            }
        )
    )

    # ChoiceField con widget Select - genera un dropdown
    # attrs={'class': 'form-control'} aplica estilos de Bootstrap
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        required=True
    )

    class Meta:
        model = Task
        # Campos que se incluirán en el formulario
        # name es editable porque a veces el usuario quiere cambiar el título
        fields = ['name', 'description', 'priority', 'start_date', 'due_date']
        

class TaskAddForm(forms.ModelForm):
    """
    Formulario para crear una nueva tarea.
    
    Diferencias con TaskUpdateForm:
    - No tiene task_id (no existe aún la tarea).
    - Placeholders diferentes (para crear vs editar).
    - Usa la misma validación base pero para un contexto de creación.
    """
    
    name = forms.CharField(
        widget= forms.TextInput(
            attrs={ 'placeholder': 'Name your task here ...'}
        ),
        required=True  # El nombre es obligatorio
    )
    

    description = forms.CharField(
        widget= forms.Textarea(
            attrs={'rows': 3, 'placeholder': 'Describe your task here ...'}
        ),
        required=False
    )

    start_date = forms.DateTimeField(
        widget=DatePicker(
            attrs= {
                'append': 'fa fa-calendar',
                'icon_toggle': True
            }
        )
    )

    due_date = forms.DateTimeField(
        widget=DatePicker(
            attrs= {
                'append': 'fa fa-calendar',
                'icon_toggle': True
            }
        )
    )

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        required=True
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'priority', 'start_date', 'due_date']
