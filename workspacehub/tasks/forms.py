from django import forms
from django.contrib.auth.models import User
from tempus_dominus.widgets import DatePicker
from .models import Task
from projects.extra import STATUS_CHOICES, PRIORITY_CHOICES


class TaskUpdateForm(forms.ModelForm):
    # hidden input
    task_id = forms.CharField(widget=forms.HiddenInput(), required=True)

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
        

class TaskAddForm(forms.ModelForm):
    
    name = forms.CharField(
        widget= forms.TextInput(
            attrs={ 'placeholder': 'Name your task here ...'}
        ),
        required=True
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
