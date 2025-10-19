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
    TIME_CHOICES = [
        ('07:00:00', '07:00 - 08:30'),
        ('08:50:00', '08:50 - 10:20'),
        ('10:30:00', '10:30 - 12:00'),
        ('13:00:00', '13:00 - 14:30'),
        ('14:50:00', '14:50 - 16:20'),
        ('16:30:00', '16:30 - 18:00'),
    ]

    horario = forms.TimeField(widget=forms.Select(choices=TIME_CHOICES))
    computador = forms.ModelChoiceField(queryset=Computador.objects.none(), required=False)

    class Meta:
        model = Reserva
        fields = ['data', 'horario', 'sala', 'computador', 'motivo']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'sala': forms.HiddenInput(),  # será preenchido pela view
            'motivo': forms.Textarea(attrs={'rows':3}),
        }

    def __init__(self, *args, sala=None, **kwargs):
        super().__init__(*args, **kwargs)
        if sala:
            self.fields['computador'].queryset = Computador.objects.filter(sala=sala)
        else:
            self.fields['computador'].queryset = Computador.objects.all()