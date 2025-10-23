from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from .models import Reserva, Sala, Computador, Usuario
from .forms import UsuarioForm, LoginForm, ReservaForm
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
@login_required
def index(request):
    return render(request,"SARC/index.html")

@login_required
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

@login_required
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

@login_required
def reservar_sala(request, id_sala=None):
    sala = None
    if id_sala is not None:
        sala = get_object_or_404(Sala, id_sala=id_sala)

    # bloquear acesso se usuário não logado (usa sua sessão)
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        request.session.pop('usuario_id', None)
        return redirect('login')

    if request.method == 'POST':
        form = ReservaForm(request.POST, sala=sala)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = usuario
            reserva.save()
            return redirect('reservas')
    else:
        form = ReservaForm(initial={'sala': sala}, sala=sala)

    # Obter todos os computadores para a sala específica ou todas as salas
    if sala:
        computadores = Computador.objects.filter(sala=sala)
    else:
        computadores = Computador.objects.all()

    context = {
        'sala': sala,
        'computadores': computadores,
        'form': form,
    }
    return render(request, "SARC/reservar_sala.html", context)


@login_required
def editar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    # bloquear acesso se usuário não logado (usa sua sessão)
    usuario_id = request.session.get('usuario_id')
    if not usuario_id or reserva.usuario.id_usuario != usuario_id:
        return redirect('login')

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva, sala=reserva.sala)
        if form.is_valid():
            form.save()
            return redirect('reservas')
    else:
        form = ReservaForm(instance=reserva, sala=reserva.sala)

    computadores = Computador.objects.filter(sala=reserva.sala)
    context = {
        'reserva': reserva,
        'computadores': computadores,
        'form': form,
    }
    return render(request, "SARC/editar_reserva.html", context)

@login_required
def cancelar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    # bloquear acesso se usuário não logado (usa sua sessão)
    usuario_id = request.session.get('usuario_id')
    if not usuario_id or reserva.usuario.id_usuario != usuario_id:
        return redirect('login')

    if request.method == 'POST':
        reserva.delete()
        return redirect('reservas')

    context = {
        'reserva': reserva,
    }
    return render(request, "SARC/cancelar_reserva.html", context)