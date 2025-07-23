from django.db import models

# Create your models here.
class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    data = models.DateField()
    horario = models.TimeField()
    sala = models.CharField(max_length=100)
    motivo = models.TextField()
    presenca = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.data} {self.horario} - {self.sala} - {self.motivo} - {'Presente' if self.presenca else 'Ausente'}"
    
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=100)

    def __str__(self):
        return f"Usuário {self.id_usuario} - {self.nome} - {self.email}"
    
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

    def __str__(self):
        return f"Computador {self.id_computador} - Sala: {self.sala.nome} - Número: {self.numero}"