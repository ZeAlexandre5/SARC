from django.shortcuts import render,redirect
from datetime import date
from .models import Reserva,Sala,Computador,Usuario
from .forms import UsuarioForm,LoginForm
from django.contrib.auth.decorators import login_required
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

def login(request):
    erro = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            matricula = form.cleaned_data['matricula']
            senha = form.cleaned_data['senha']
            try:
                usuario = Usuario.objects.get(matricula=matricula, senha=senha)
                request.session['usuario_id'] = usuario.id_usuario  # Salva o id do usuário na sessão
                request.session['usuario_nome'] = usuario.nome
                return redirect('reservas')
            except Usuario.DoesNotExist:
                erro = "Matrícula ou senha inválidos."
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
        return redirect('login')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    reservas = Reserva.objects.filter(usuario=usuario)
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


