from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario, Reserva, Sala, Computador

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'matricula', 'email', 'senha']  # ajuste os campos conforme seu model
        widgets = {
            'senha': forms.PasswordInput(),
        }

class LoginForm(forms.Form):
    matricula = forms.CharField(max_length=20)
    senha = forms.CharField(widget=forms.PasswordInput())

    def clean_usuario(self):
        cleaned_data = super().clean()
        matricula = cleaned_data.get('matricula')
        senha = cleaned_data.get('senha')
        
        if matricula and senha:
            try:
                usuario = Usuario.objects.get(matricula=matricula, senha=senha)
            except Usuario.DoesNotExist:
                raise forms.ValidationError("Matrícula ou senha inválidos.")
        
        return cleaned_data

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade']

class ComputadorForm(forms.ModelForm):
    class Meta:
        model = Computador
        fields = ['sala', 'numero', 'estado']

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['data', 'horario', 'sala', 'motivo']

        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }