from django.contrib import admin
from .models import Reserva, Usuario, Sala, Computador

# Register your models here.
admin.site.register(Reserva)
admin.site.register(Usuario)
admin.site.register(Sala)
admin.site.register(Computador)