from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class UsuarioManager(BaseUserManager):
    """
    Manager custom para Usuario que usa 'matricula' como identificador.
    """
    use_in_migrations = True

    def _create_user(self, matricula, email, password, **extra_fields):
        if not matricula:
            raise ValueError('The given matricula must be set')
        email = self.normalize_email(email)
        user = self.model(matricula=matricula, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, matricula, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(matricula, email, password, **extra_fields)

    def create_superuser(self, matricula, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(matricula, email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Usuário custom baseado em AbstractUser.
    Mantemos a coluna existente 'id_usuario' no banco como primary key
    e reutilizamos a coluna 'senha' (db_column='senha').
    """
    # garante compatibilidade com a tabela existente que tem id_usuario como PK
    id = models.AutoField(primary_key=True, db_column='id_usuario')

    # reutilizar coluna de senha já existente
    password = models.CharField(max_length=128, db_column='senha')

    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nome = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    

    TIPO_USUARIO_CHOICES = [
        ('bolsista', 'Bolsista'),
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
    ]
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='aluno')

    USERNAME_FIELD = 'matricula'
    REQUIRED_FIELDS = ['email']

    objects = UsuarioManager()

    @property
    def id_usuario(self):
        return self.pk

    def __str__(self):
        return f"{self.nome or self.get_full_name() or self.username} ({self.matricula})"

class Sala(models.Model):
    id_sala = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField()

    def __str__(self):
        return f"Sala {self.id_sala} - {self.nome} - Capacidade: {self.capacidade}"
    
class Computador(models.Model):
    id_computador = models.AutoField(primary_key=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    numero = models.CharField(max_length=10)
    estado = models.CharField(max_length=20, default='Disponível') 


    def __str__(self):
        return f"Computador {self.id_computador} - Sala: {self.sala.nome} - Número: {self.numero}"
    
class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data = models.DateField()
    horario = models.TimeField()
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    computador = models.ForeignKey(Computador, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.TextField()
    # Novo campo para presença
    PRESENCA_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('pendente', 'Pendente'),
    ]
    presenca = models.CharField(
        max_length=10,
        choices=PRESENCA_CHOICES,
        default='pendente'
    )

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.data} {self.horario} - {self.sala} - {self.motivo} - {'Presente' if self.presenca == 'presente' else 'Ausente' if self.presenca == 'ausente' else 'Pendente'}"
# (Removida qualquer definição de Form que estivesse dentro deste arquivo;
#  formulários devem ficar em SARC/forms.py)