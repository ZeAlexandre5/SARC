from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,"index.html")

def reserva(request):
    return render(request,"reservas.html")

def salas(request):
    return render(request,"salas.html")