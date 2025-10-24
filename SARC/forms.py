from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario, Reserva, Sala, Computador

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['matricula', 'nome', 'email', 'senha', 'tipo_usuario']
        widgets = {
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'senha': forms.PasswordInput(attrs={'class': 'form-control'}),  # aqui: input type="password"
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
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

    horario = forms.TimeField(
        widget=forms.Select(choices=TIME_CHOICES),
        label="Horário"
    )
    computador = forms.ModelChoiceField(
        queryset=Computador.objects.none(), 
        required=False,  # Computador não é obrigatório
        widget=forms.HiddenInput(),
        label="Computador"
    )
    
    # TORNAR SALA NÃO OBRIGATÓRIA NO FORMULÁRIO, POIS JÁ VEM DA URL
    sala = forms.ModelChoiceField(
        queryset=Sala.objects.all(),
        required=False,  # Não é obrigatório no formulário
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
        
        # Se uma sala foi passada, define ela como valor inicial
        if sala:
            self.fields['sala'].initial = sala
            self.fields['computador'].queryset = Computador.objects.filter(sala=sala)
        else:
            self.fields['computador'].queryset = Computador.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        
        # Obter a sala do initial se não veio do formulário
        sala = cleaned_data.get('sala') or self.fields['sala'].initial
        computador = cleaned_data.get('computador')
        data = cleaned_data.get('data')
        horario = cleaned_data.get('horario')

        # Verificar se a sala foi definida
        if not sala:
            raise ValidationError("Sala não especificada.")

        # Verificar se computador pertence à sala
        if computador and computador.sala != sala:
            raise ValidationError("Computador selecionado não pertence à sala.")

        # Verificar conflitos de reserva
        if data and horario:
            conflito = Reserva.objects.filter(
                sala=sala, 
                data=data, 
                horario=horario
            )
            # Se um computador específico foi selecionado, verificar conflito para ele
            if computador:
                conflito = conflito.filter(computador=computador)
            
            # Excluir a própria reserva se estiver editando
            if self.instance and self.instance.pk:
                conflito = conflito.exclude(pk=self.instance.pk)
                
            if conflito.exists():
                if computador:
                    raise ValidationError("Computador já reservado para esse horário.")
                else:
                    raise ValidationError("Já existe uma reserva para esta sala e horário.")
        
        return cleaned_data