from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request,"SARC/index.html")

def reserva(request):
    return render(request,"SARC/reservas.html")

def salas(request):
    return render(request,"SARC/salas.html")

def cadastro(request):
    return render(request,"SARC/cadastro.html")

def reservar_sala(request):
    return render(request,"SARC/reservar_sala.html")