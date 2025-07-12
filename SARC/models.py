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