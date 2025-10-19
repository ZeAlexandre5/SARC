from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario, Reserva, Sala, Computador

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'matricula', 'email', 'senha', 'tipo_usuario']
        widgets = {
            'senha': forms.PasswordInput(),
            'tipo_usuario': forms.Select(),
        }

class LoginForm(forms.Form):
    matricula = forms.CharField(max_length=20)
    senha = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned = super().clean()
        matricula = cleaned.get('matricula')
        senha = cleaned.get('senha')
        if matricula and senha:
            try:
                usuario = Usuario.objects.get(matricula=matricula, senha=senha)
                self.user = usuario  # disponível para a view após validação
            except Usuario.DoesNotExist:
                raise forms.ValidationError("Matrícula ou senha inválidos.")
        return cleaned

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