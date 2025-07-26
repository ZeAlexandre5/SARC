from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request,"index.html")

def reserva(request):
    return render(request,"Sarc/reservas.html")

def salas(request):
    return render(request,"Sarc/salas.html")

def cadastro(request):
    return render(request,"Sarc/cadastro.html")

def reservar_sala(request):
    return render(request,"Sarc/reservar_sala.html")