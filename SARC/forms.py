from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'matricula', 'email', 'senha']  # ajuste os campos conforme seu model
        widgets = {
            'senha': forms.PasswordInput(),
        }