from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, timedelta, date
from django.utils import timezone
from .models import Reserva, Sala, Computador, Usuario
from .forms import UsuarioForm, LoginForm, ReservaForm, ProfessorReservaForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import login as auth_login


# helper: atualiza automaticamente reservas pendentes para 'ausente' após 24h do horário agendado
def _auto_mark_absent():
    now = timezone.now()
    cutoff = now - timedelta(hours=24)
    pendentes = Reserva.objects.filter(presenca='pendente')
    for r in pendentes:
        try:
            scheduled = datetime.combine(r.data, r.horario)
            if timezone.is_naive(scheduled):
                scheduled = timezone.make_aware(scheduled, timezone.get_current_timezone())
        except Exception:
            continue
        if scheduled < cutoff:
            r.presenca = 'ausente'
            r.save(update_fields=['presenca'])

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

            # LOGIN REAL DO DJANGO
            auth_login(request, usuario)

            # redireciona conforme tipo
            if usuario.tipo_usuario == 'bolsista':
                return redirect('dashboard_bolsista')

            return redirect('reservas')
        else:
            erro = "Matrícula ou senha inválidos."
    else:
        form = LoginForm()

    return render(request, "SARC/Login.html", {'form': form, 'erro': erro})

# Create your views here.

def index(request):
    return render(request,"SARC/index.html")

@login_required
def reserva(request):
    # atualiza ausências antes de listar
    _auto_mark_absent()

    usuario = request.user
    if not request.user.is_authenticated:
        return redirect('login')

    try:
       usuario = request.user
    except Usuario.DoesNotExist:
        return redirect('login')

    # bolsista vê todas as reservas, outros só as próprias
    if usuario.tipo_usuario == 'bolsista':
        reservas = Reserva.objects.all().order_by('-data', '-horario')
    else:
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
    else:
        salas = Sala.objects.all()
        if salas.exists():
            sala = salas.first()
        else:
            messages.error(request, 'Nenhuma sala cadastrada no sistema.')
            return redirect('salas')

    usuario = request.user
    if not request.user.is_authenticated:
        messages.error(request, 'Você precisa fazer login para reservar.')
        return redirect('login')
    try:
        usuario = request.user
    except Usuario.DoesNotExist:
        messages.error(request, 'Sessão expirada. Faça login novamente.')
        return redirect('login')

    tipo_usuario = usuario.tipo_usuario

    if request.method == 'POST':
        print("DEBUG - Dados do POST:", request.POST)
        data = request.POST.copy()  # mutável

        # Professores não escolhem computador nem precisam preencher motivo:
        if tipo_usuario == 'professor':
            # garantir motivo mínimo para o form
            if not data.get('motivo'):
                data['motivo'] = 'Reserva de sala (Professor)'
            # garantir computador vazio
            data['computador'] = ''

        # Bolsista pode bloquear sala: checkbox name="bloquear"
        if tipo_usuario == 'bolsista' and data.get('bloquear') == 'on':
            # marca como bloqueio caso não haja motivo
            if not data.get('motivo'):
                data['motivo'] = 'Bloqueio de sala (Bolsista)'
            data['computador'] = ''  # bloqueio sem computador

        form = ReservaForm(data, sala=sala)

        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = usuario

            # assegurar sala se vier pela URL
            if not reserva.sala and sala:
                reserva.sala = sala

            # forçar comportamento: professores/bolsistas sem computador
            if tipo_usuario in ['professor', 'bolsista']:
                reserva.computador = None

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
        'tipo_usuario': tipo_usuario,  # necessário no template
    }
    return render(request, "SARC/reservar_sala.html", context)

@login_required
def editar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    # bloquear acesso se usuário não logado (usa sua sessão)
    usuario = request.user
    if not request.user.is_authenticated or reserva.usuario != request.user:
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
    usuario = request.user
    if not usuario.is_authenticated or reserva.usuario != usuario:
        return redirect('login')

    if request.method == 'POST':
        reserva.delete()
        return redirect('reservas')

    context = {
        'reserva': reserva,
    }
    return render(request, "SARC/cancelar_reserva.html", context)

@login_required
def dashboard_bolsista(request):
    usuario = request.user
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        usuario = request.user
        # Verificar se é bolsista
        if usuario.tipo_usuario != 'bolsista':
            return redirect('reservas')
    except Usuario.DoesNotExist:
        return redirect('login')
    
    # Estatísticas
    total_reservas = Reserva.objects.count()
    hoje = date.today()
    reservas_hoje = Reserva.objects.filter(data=hoje).count()
    
    # Calcular salas ocupadas hoje
    salas_ocupadas_ids = Reserva.objects.filter(data=hoje).values_list('sala', flat=True).distinct()
    salas_ocupadas = len(salas_ocupadas_ids)
    
    # Para simplificar, vamos considerar que salas bloqueadas são aquelas com reserva de bolsista
    salas_bloqueadas = Reserva.objects.filter(
        data=hoje, 
        usuario__tipo_usuario='bolsista',
        motivo__icontains='bloqueio'
    ).count()
    
    # Reservas recentes (últimas 10)
    reservas = Reserva.objects.all().order_by('-data', '-horario')[:10]
    
    # Status das salas (simplificado)
    salas = Sala.objects.all()
    for sala in salas:
        reserva_hoje = Reserva.objects.filter(sala=sala, data=hoje).exists()
        if reserva_hoje:
            sala.status = 'ocupada'
        else:
            sala.status = 'disponivel'
    
    context = {
        'total_reservas': total_reservas,
        'reservas_hoje': reservas_hoje,
        'salas_ocupadas': salas_ocupadas,
        'salas_bloqueadas': salas_bloqueadas,
        'reservas': reservas,
        'salas': salas,
        'hoje': hoje,
    }
    
    return render(request, "SARC/dashboard_bolsista.html", context)

@login_required
def marcar_presenca(request, id_reserva):
    if request.method != 'POST':
        return redirect('reservas')

    usuario = request.user
    if not request.user.is_authenticated:
        messages.error(request, 'Faça login para registrar presença.')
        return redirect('login')

    usuario = request.user
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    # autorização: bolsista pode marcar qualquer; usuário normal só marcar suas reservas
    if usuario.tipo_usuario != 'bolsista' and reserva.usuario != usuario:

        messages.error(request, 'Você não tem permissão para marcar presença nesta reserva.')
        return redirect('reservas')

    # auto-update ausências (por segurança)
    _auto_mark_absent()

    if reserva.presenca == 'presente':
        messages.info(request, 'Presença já registrada.')
        return redirect('reservas')

    # impedir marcar presença se já expirou (mais de 24h)
    try:
        scheduled = datetime.combine(reserva.data, reserva.horario)
        if timezone.is_naive(scheduled):
            scheduled = timezone.make_aware(scheduled, timezone.get_current_timezone())
    except Exception:
        scheduled = None

    now = timezone.now()
    if scheduled and scheduled + timedelta(hours=24) < now:
        messages.error(request, 'Prazo para registrar presença expirado; status ficou como falta.')
        return redirect('reservas')

    reserva.presenca = 'presente'
    reserva.save(update_fields=['presenca'])
    messages.success(request, 'Presença registrada com sucesso.')
    return redirect('reservas')

def check_availability(request):
    """
    GET params: sala_id (int), date (YYYY-MM-DD), horario (HH:MM:SS or HH:MM)
    Retorna JSON: { "reserved_all": bool, "reserved": [id_computador,...] }
    """
    sala_id = request.GET.get('sala_id')
    date_str = request.GET.get('date')
    horario = request.GET.get('horario')

    if not sala_id or not date_str or not horario:
        return JsonResponse({'error': 'missing parameters'}, status=400)

    try:
        # data no formato ISO 'YYYY-MM-DD'
        from datetime import datetime
        data = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return JsonResponse({'error': 'invalid date'}, status=400)

    # normalizar horario para HH:MM:SS se necessário
    if len(horario) == 5:
        horario = horario + ':00'

    # buscar reservas nessa sala/data/horario
    reservas = Reserva.objects.filter(sala_id=sala_id, data=data, horario=horario)
    reserved_all = reservas.filter(computador__isnull=True).exists()
    reserved_ids = list(reservas.exclude(computador__isnull=True).values_list('computador_id', flat=True))

    return JsonResponse({'reserved_all': reserved_all, 'reserved': reserved_ids})

@require_POST
@login_required
def bloquear_sala(request):
    """Bloquear sala — usado pelo bolsista. Recebe sala_id, date, horario, motivo via POST (AJAX)."""
    usuario = request.user
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    usuario = request.user
    if usuario.tipo_usuario != 'bolsista':
        return JsonResponse({'error': 'forbidden'}, status=403)

    sala_id = request.POST.get('sala_id') or request.POST.get('sala')
    date_str = request.POST.get('data') or request.POST.get('date')
    horario = request.POST.get('horario')
    motivo = request.POST.get('motivo') or 'Bloqueio de sala (Bolsista)'

    if not sala_id or not date_str or not horario:
        return JsonResponse({'error': 'missing_parameters'}, status=400)

    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return JsonResponse({'error': 'invalid_date'}, status=400)

    if len(horario) == 5:
        horario = horario + ':00'

    # não duplicar bloqueio
    conflito = Reserva.objects.filter(sala_id=sala_id, data=d, horario=horario)
    if conflito.filter(computador__isnull=True).exists():
        return JsonResponse({'error': 'already_blocked'}, status=409)

    # criar reserva sem computador indicando bloqueio
    reserva = Reserva(
        usuario=usuario,
        data=d,
        horario=horario,
        sala_id=sala_id,
        computador=None,
        motivo=motivo
    )
    reserva.save()
    return JsonResponse({'success': True, 'id_reserva': reserva.id_reserva})


@require_POST
@login_required
def desbloquear_sala(request):
    """Desbloquear sala — remove reserva de bloqueio (bolsista) para sala/data/horário."""
    usuario = request.user
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    usuario = request.user
    if usuario.tipo_usuario != 'bolsista':
        return JsonResponse({'error': 'forbidden'}, status=403)

    sala_id = request.POST.get('sala_id')
    date_str = request.POST.get('data')
    horario = request.POST.get('horario')

    if not sala_id or not date_str or not horario:
        return JsonResponse({'error': 'missing_parameters'}, status=400)

    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return JsonResponse({'error': 'invalid_date'}, status=400)

    if len(horario) == 5:
        horario = horario + ':00'

    bloqueios = Reserva.objects.filter(
        sala_id=sala_id, data=d, horario=horario, computador__isnull=True,
        usuario__tipo_usuario='bolsista'
    )
    if not bloqueios.exists():
        return JsonResponse({'error': 'no_block_found'}, status=404)

    count = bloqueios.count()
    bloqueios.delete()
    return JsonResponse({'success': True, 'deleted': count})


@require_POST
@login_required
def editar_reserva_ajax(request):
    """Editar reserva via AJAX — bolsista pode editar qualquer; usuário pode editar a sua."""
    usuario = request.user
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    usuario = request.user

    try:
        payload = request.POST
        reserva_id = payload.get('id') or payload.get('id_reserva')
        reserva = Reserva.objects.get(id_reserva=reserva_id)
    except Exception:
        return JsonResponse({'error': 'invalid_reserva'}, status=400)

    # permissão
    if usuario.tipo_usuario != 'bolsista' and reserva.usuario != usuario:
        return JsonResponse({'error': 'forbidden'}, status=403)

    # aplicar alterações permitidas
    data_str = payload.get('data')
    horario = payload.get('horario')
    motivo = payload.get('motivo')

    if data_str:
        try:
            reserva.data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except Exception:
            return JsonResponse({'error': 'invalid_date'}, status=400)
    if horario:
        reserva.horario = horario if len(horario) == 8 else horario + ':00'
    if motivo is not None:
        reserva.motivo = motivo

    reserva.save()
    return JsonResponse({'success': True, 'id_reserva': reserva.id_reserva})


@require_POST
@login_required
def cancelar_reserva_ajax(request):
    """Cancelar reserva via AJAX."""
    usuario = request.user
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    usuario = request.user


    reserva_id = request.POST.get('id') or request.POST.get('id_reserva')
    try:
        reserva = Reserva.objects.get(id_reserva=reserva_id)
    except Reserva.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)

    if usuario.tipo_usuario != 'bolsista' and reserva.usuario != usuario:
        return JsonResponse({'error': 'forbidden'}, status=403)

    reserva.delete()
    return JsonResponse({'success': True})
