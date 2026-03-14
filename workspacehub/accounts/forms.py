
"""
Formularios de la aplicación accounts.

Contiene el formulario de registro de usuarios.
"""

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """
    Formulario para el registro de nuevos usuarios.
    
    ¿Por qué heredar de UserCreationForm en lugar de crear desde cero?
    - Ya incluye validación de contraseña robusta (mayúsculas, números, caracteres especiales).
    - Tiene campos de contraseña y confirmación de contraseña con verificación.
    - Maneja de forma segura el hashing de contraseñas.
    - Reduce significativamente el código necesario.
    
    Campos incluidos:
    - username: Nombre de usuario único
    - email: Correo electrónico del usuario
    - password1: Contraseña
    - password2: Confirmación de contraseña
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        """
        Personalización del formulario para mejorar la experiencia de usuario.
        
        ¿Por qué sobrescribir __init__?
        - Los campos de UserCreationForm tienen ayuda textual extensa por defecto.
        - Para un formulario de registro, esa información puede ser confusa o innecesaria.
        - Eliminamos help_text para un diseño más limpio.
        """
        super().__init__(*args, **kwargs)

        # removing helper text
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
    