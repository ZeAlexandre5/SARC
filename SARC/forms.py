from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario, Reserva, Sala, Computador

# ==========================
# FORMULÁRIO DE USUÁRIO
# ==========================
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['matricula', 'nome', 'email', 'senha', 'tipo_usuario']
        widgets = {
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'senha': forms.PasswordInput(attrs={'class': 'form-control'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
        }


# ==========================
# FORMULÁRIO DE LOGIN
# ==========================
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
                self.user = usuario
            except Usuario.DoesNotExist:
                raise forms.ValidationError("Matrícula ou senha inválidos.")
        return cleaned


# ==========================
# FORMULÁRIO DE SALA
# ==========================
class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade']


# ==========================
# FORMULÁRIO DE COMPUTADOR
# ==========================
class ComputadorForm(forms.ModelForm):
    class Meta:
        model = Computador
        fields = ['sala', 'numero', 'estado']


# ==========================
# FORMULÁRIO DE RESERVA (ALUNO)
# ==========================
class ReservaForm(forms.ModelForm):
    TIME_CHOICES = [
        ('07:00:00', '07:00 - 08:30'),
        ('08:50:00', '08:50 - 10:20'),
        ('10:30:00', '10:30 - 12:00'),
        ('13:00:00', '13:00 - 14:30'),
        ('14:50:00', '14:50 - 16:20'),
        ('16:30:00', '16:30 - 18:00'),
    ]

    horario = forms.TimeField(
        widget=forms.Select(choices=TIME_CHOICES),
        label="Horário"
    )

    computador = forms.ModelChoiceField(
        queryset=Computador.objects.none(),
        required=False,
        widget=forms.HiddenInput(),
        label="Computador"
    )

    sala = forms.ModelChoiceField(
        queryset=Sala.objects.all(),
        required=False,
        widget=forms.HiddenInput(),
        label="Sala"
    )

    class Meta:
        model = Reserva
        fields = ['data', 'horario', 'sala', 'computador', 'motivo']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Digite o motivo da reserva...'}),
        }
        labels = {
            'data': 'Data da Reserva:',
            'motivo': 'Motivo da Reserva:',
        }

    def __init__(self, *args, sala=None, **kwargs):
        super().__init__(*args, **kwargs)
        if sala:
            self.fields['sala'].initial = sala
            self.fields['computador'].queryset = Computador.objects.filter(sala=sala)
        else:
            self.fields['computador'].queryset = Computador.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        sala = cleaned_data.get('sala') or self.fields['sala'].initial
        computador = cleaned_data.get('computador')
        data = cleaned_data.get('data')
        horario = cleaned_data.get('horario')

        # Impedir reserva para data passada
        if data:
            hoje = timezone.localdate()
            if data < hoje:
                raise ValidationError("Não é possível reservar para dias no passado.")

        if not sala:
            raise ValidationError("Sala não especificada.")

        if computador and computador.sala != sala:
            raise ValidationError("Computador selecionado não pertence à sala.")

        if data and horario:
            conflito = Reserva.objects.filter(sala=sala, data=data, horario=horario)
            if computador:
                conflito = conflito.filter(computador=computador)
            if self.instance and self.instance.pk:
                conflito = conflito.exclude(pk=self.instance.pk)
            if conflito.exists():
                raise ValidationError("Já existe uma reserva para esta sala e horário.")

        return cleaned_data


# ==========================
# FORMULÁRIO DE RESERVA (PROFESSOR)
# ==========================
class ProfessorReservaForm(forms.ModelForm):
    TIME_CHOICES = [
        ('07:00:00', '07:00 - 08:30'),
        ('08:50:00', '08:50 - 10:20'),
        ('10:30:00', '10:30 - 12:00'),
        ('13:00:00', '13:00 - 14:30'),
        ('14:50:00', '14:50 - 16:20'),
        ('16:30:00', '16:30 - 18:00'),
    ]

    horario = forms.TimeField(
        widget=forms.Select(choices=TIME_CHOICES),
        label="Horário"
    )

    sala = forms.ModelChoiceField(
        queryset=Sala.objects.all(),
        required=True,
        label="Sala",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Reserva
        fields = ['data', 'horario', 'sala', 'motivo']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Motivo da reserva'}),
        }
        labels = {
            'data': 'Data da Reserva:',
            'motivo': 'Motivo da Reserva:',
        }

    def clean(self):
        cleaned_data = super().clean()
        sala = cleaned_data.get('sala')
        data = cleaned_data.get('data')
        horario = cleaned_data.get('horario')

        # Impedir reserva para data passada
        if data:
            hoje = timezone.localdate()
            if data < hoje:
                raise ValidationError("Não é possível reservar para dias no passado.")

        if data and horario and sala:
            conflito = Reserva.objects.filter(
                sala=sala,
                data=data,
                horario=horario
            ).exclude(pk=self.instance.pk if self.instance else None)

            if conflito.exists():
                raise ValidationError("Já existe uma reserva para esta sala e horário.")

        return cleaned_data



