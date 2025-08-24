from django.shortcuts import render
from datetime import date
from .models import Reserva,Sala,Computador
from .forms import UsuarioForm
# ...existing code...

def cadastro(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "SARC/cadastro.html", {'form': form, 'success': True})
    else:
        form = UsuarioForm()
    return render(request, "SARC/cadastro.html", {'form': form})
# ...existing code...

# Create your views here.
def index(request):
    return render(request,"SARC/index.html")

def reserva(request):
    reservas = Reserva.objects.all()
    today = date.today()
    reservas = reservas.filter(data=today)
    context = {
        'reservas': reservas,
    }
    return render(request,"SARC/reservas.html", context)

def salas(request):
    today = date.today()
    reservas = Reserva.objects.filter(data=today)
    salas = Sala.objects.all()
    computadores = Computador.objects.all()
    context = {
        'salas': salas,
        'computadores': computadores,
        'reservas': reservas,
    }
    return render(request, "SARC/salas.html", context)


def reservar_sala(request):
    return render(request,"SARC/reservar_sala.html")