from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from .models import Reserva, Sala, Computador, Usuario
from .forms import UsuarioForm, LoginForm, ReservaForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

@login_required
def reserva(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        request.session.pop('usuario_id', None)
        return redirect('login')

    reservas = Reserva.objects.filter(usuario=usuario).order_by('-data', '-horario')
    
    # DEBUG: Mostrar no console
    print(f"DEBUG - Reservas do usuário {usuario.nome}:")
    for r in reservas:
        print(f"  - {r.data} {r.horario} | Sala: {r.sala.nome} | Computador: {r.computador.numero if r.computador else 'Nenhum'}")
    
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
    else:
        # Se não veio pela URL, tentar pegar da primeira sala disponível
        salas = Sala.objects.all()
        if salas.exists():
            sala = salas.first()
        else:
            messages.error(request, 'Nenhuma sala cadastrada no sistema.')
            return redirect('salas')

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Você precisa fazer login para reservar.')
        return redirect('login')

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        request.session.pop('usuario_id', None)
        messages.error(request, 'Sessão expirada. Faça login novamente.')
        return redirect('login')

    if request.method == 'POST':
        print("DEBUG - Dados do POST:", request.POST)
        
        form = ReservaForm(request.POST, sala=sala)
        
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = usuario
            
            # Garantir que a sala está definida
            if not reserva.sala and sala:
                reserva.sala = sala
                
            print(f"DEBUG - Salvando reserva:")
            print(f"  Usuário: {reserva.usuario.nome}")
            print(f"  Data: {reserva.data}")
            print(f"  Horário: {reserva.horario}")
            print(f"  Sala: {reserva.sala.nome if reserva.sala else 'None'}")
            print(f"  Computador: {reserva.computador.numero if reserva.computador else 'None'}")
            print(f"  Motivo: {reserva.motivo}")
            
            try:
                reserva.save()
                messages.success(request, f'Reserva realizada com sucesso!')
                return redirect('reservas')
            except Exception as e:
                messages.error(request, f'Erro ao salvar reserva: {str(e)}')
        else:
            print("DEBUG - Erros do formulário:", form.errors)
            messages.error(request, 'Erro no formulário. Verifique os dados.')
            
    else:
        form = ReservaForm(initial={'sala': sala}, sala=sala)

    salas = Sala.objects.all().prefetch_related('computador_set')
    computadores = Computador.objects.all()
    
    if sala:
        computadores = computadores.filter(sala=sala)

    context = {
        'sala': sala,
        'salas': salas,
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

@login_required
def reservar_sala_professor(request):
    """
    View que permite ao professor reservar uma sala sem computador.
    """
    # Tenta identificar o usuário logado como Professor
    try:
        usuario = Usuario.objects.get(matricula=request.user.matricula)
    except Exception:
        usuario = None

    if request.method == 'POST':
        form = ProfessorReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            if usuario:
                reserva.usuario = usuario  # associa ao professor logado
            else:
                reserva.usuario = request.user  # fallback

            reserva.save()
            messages.success(request, "Sala reservada com sucesso!")
            return redirect('minhas_reservas')  # ajuste o nome da URL
        else:
            messages.error(request, "Corrija os erros no formulário.")
    else:
        form = ProfessorReservaForm()

    return render(request, 'reservar_sala_professor.html', {'form': form})

