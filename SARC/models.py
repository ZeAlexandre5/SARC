from django.db import models
from django import forms
# Create your models here.
    
class Usuario(models.Model):
    
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)

    TIPO_USUARIO_CHOICES = [
        ('bolsista', 'Bolsista'),
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
    ]
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='aluno')
    def __str__(self):
        return f"Usuário {self.id_usuario} - {self.nome} - {self.email} - Matrícula: {self.matricula}"

class Sala(models.Model):
    id_sala = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField()

    def __str__(self):
        return f"Sala {self.id_sala} - {self.nome} - Capacidade: {self.capacidade}"
    
class Computador(models.Model):
    id_computador = models.AutoField(primary_key=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    numero = models.CharField(max_length=10)
    estado = models.CharField(max_length=20, default='Disponível') 


    def __str__(self):
        return f"Computador {self.id_computador} - Sala: {self.sala.nome} - Número: {self.numero}"
    
class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data = models.DateField()
    horario = models.TimeField()
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    computador = models.ForeignKey(Computador, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.TextField()
    # Novo campo para presença
    PRESENCA_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('pendente', 'Pendente'),
    ]
    presenca = models.CharField(
        max_length=10,
        choices=PRESENCA_CHOICES,
        default='pendente'
    )

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.data} {self.horario} - {self.sala} - {self.motivo} - {'Presente' if self.presenca == 'presente' else 'Ausente' if self.presenca == 'ausente' else 'Pendente'}"

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['matricula', 'nome', 'email', 'senha']
        widgets = {
            'senha': forms.PasswordInput(),  # Campo de senha oculto
        }