from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from .models import Reserva, Sala, Computador, Usuario
from .forms import UsuarioForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# ...existing code...
def index(request):
    return render(request, 'index.html')  # ← 4 espaços de indentação


def cadastro(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "SARC/cadastro.html", {'form': form, 'success': True})
    else:
        form = UsuarioForm()
    return render(request, "SARC/cadastro.html", {'form': form})

def login(request):
    erro = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.user
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nome'] = usuario.nome
            return redirect('reservas')
        else:
            # erros do form aparecem automaticamente; opcionalmente repassar mensagem genérica
            erro = None
    else:
        form = LoginForm()
    return render(request, "SARC/Login.html", {'form': form, 'erro': erro})
# ...existing code...

# Create your views here.
def index(request):
    return render(request,"SARC/index.html")

def reserva(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')  # redireciona para sua página de login

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        request.session.pop('usuario_id', None)
        return redirect('login')

    reservas = Reserva.objects.filter(usuario=usuario).order_by('-data', '-horario')
    context = {
        'reservas': reservas,
        'usuario': usuario,
    }
    return render(request, "SARC/reservas.html", context)

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


def reservar_sala(request, id_sala=None):
    # se id_sala fornecido, carrega a sala; senão mostra lista ou erro
    sala = None
    computadores = None
    if id_sala is not None:
        sala = get_object_or_404(Sala, id_sala=id_sala)
        computadores = Computador.objects.filter(sala=sala)
    context = {
        'sala': sala,
        'computadores': computadores,
    }
    return render(request, "SARC/reservar_sala.html", context)


