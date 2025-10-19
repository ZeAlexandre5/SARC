from django.shortcuts import render,redirect,get_object_or_404
from datetime import date
from .models import Reserva,Sala,Computador,Usuario
from .forms import UsuarioForm,LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# ...existing code...
def index(request):
    return render(request, 'index.html')  # ← 4 espaços de indentação

def login_view(request):
    erro = None
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        senha = request.POST.get('senha')

        # Autenticação do usuário
        user = authenticate(request, username=matricula, password=senha)
        if user is not None:
            login(request, user)  # Faz login do usuário

            # Verifica o tipo de usuário e redireciona
            if user.groups.filter(name='aluno').exists():
                return redirect("home_usu")  # Nome da URL para a página do aluno
            elif user.groups.filter(name='professor').exists():
                return redirect("home_pro")  # Nome da URL para a página do professor
            elif user.groups.filter(name='bolsista').exists():
                return redirect('home_bol')  # Nome da URL para a página do bolsista
            else:
                return redirect('default_home')  # Página padrão caso não se encaixe em nenhum grupo
        else:
            erro = 'Credenciais inválidas. Tente novamente.'

    return render(request, "SARC/index.html", {'erro': erro})

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

            usuario = Usuario.objects.get(matricula=matricula, senha=senha)
            
            request.session['usuario_id'] = usuario.id_usuario  # Salva o id do usuário na sessão
            request.session['usuario_nome'] = usuario.nome
            return redirect('reservas')
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

@login_required
def home_usu(request):
    return render(request,"SARC/home_usu.html")

@login_required
def home_pro(request):
    return render(request,"SARC/home_pro.html")

@login_required
def home_bol(request):
    return render(request,"SARC/home_bol.html")
