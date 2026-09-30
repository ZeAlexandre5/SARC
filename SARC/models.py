from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, matricula, email, password, **extra_fields):
        if not matricula:
            raise ValueError('The given matricula must be set')
        email = self.normalize_email(email)
        user = self.model(matricula=matricula, email=email, **extra_fields)
        user.set_password(password)   # Agora funciona corretamente
        user.save(using=self._db)
        return user

    def create_user(self, matricula, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(matricula, email, password, **extra_fields)

    def create_superuser(self, matricula, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(matricula, email, password, **extra_fields)

class Usuario(AbstractUser):
    id = models.AutoField(primary_key=True, db_column='id_usuario')

    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nome = models.CharField(max_length=100, blank=True)
    # temporariamente permitimos null/blank para evitar prompt durante migrações
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    username = None  # removendo o campo username padrão
    TIPO_USUARIO_CHOICES = [
        ('bolsista', 'Bolsista'),
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
    ]
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='aluno')

    USERNAME_FIELD = 'matricula'
    REQUIRED_FIELDS = ['email']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

class Sala(models.Model):
    TIPO_SALA_CHOICES = [
        ('laboratorio_informatica', 'Laboratório de Informática'),
        ('sala_aula', 'Sala de Aula'),
        ('outro', 'Outro'),
    ]
    
    id_sala = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField()
    tipo = models.CharField(max_length=30, choices=TIPO_SALA_CHOICES, default='laboratorio_informatica')
    descricao = models.TextField(blank=True, null=True, help_text="Descrição da sala - obrigatória se tipo é 'Outro'")

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

    bloqueio = models.BooleanField(default=False)  

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.data} {self.horario} - {self.sala} - {self.motivo} - {'Presente' if self.presenca == 'presente' else 'Ausente' if self.presenca == 'ausente' else 'Pendente'}"

class Notificacao(models.Model):
    id_notificacao = models.AutoField(primary_key=True)
    remetente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    mensagem = models.TextField()
    resposta = models.TextField(null=True, blank=True)
    data_envio = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    lida = models.BooleanField(default=False)  # Indica se o aluno viu a resposta

    def __str__(self):
        return f"Mensagem de {self.remetente.nome} - {self.data_envio.strftime('%d/%m/%Y')}"

class DiaBloqueado(models.Model):
    bloqueio_id = models.AutoField(primary_key=True)
    data = models.DateField(unique=True)
    motivo = models.CharField(max_length=255)

    criado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dia Bloqueado: {self.data} - Motivo: {self.motivo}"


class Projeto(models.Model):
    id_projeto = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_limite = models.DateField()
    participantes = models.ManyToManyField(Usuario, related_name='projetos')
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='projetos_criados')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_limite', '-criado_em']

    def __str__(self):
        return f"Projeto #{self.id_projeto} - {self.titulo}"


class AnotacaoProjeto(models.Model):
    id_anotacao = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='anotacoes')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='anotacoes_de_projeto')
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']


class ArquivoProjeto(models.Model):
    id_arquivo = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='arquivos')
    enviado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='arquivos_de_projeto')
    arquivo = models.FileField(upload_to='projetos/%Y/%m/')
    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-enviado_em']

    @property
    def nome(self):
        return self.arquivo.name.rsplit('/', 1)[-1]


class SalaGenérica(models.Model):
    """Salas genéricas para reservas de professores (salas de aula, reuniões, etc.)"""
    id_sala_generica = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField(help_text="Capacidade máxima de alunos")
    tipo = models.CharField(max_length=30, choices=TIPO_SALA_CHOICES, default='sala_aula')
    descricao = models.TextField(blank=True, null=True, help_text="Descrição da sala - obrigatória se tipo é 'Outro'")
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    criada_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Sala Genérica"
        verbose_name_plural = "Salas Genéricas"

    def __str__(self):
        return f"{self.nome} (Cap: {self.capacidade})"


class ReservaSalaGenérica(models.Model):
    """Reservas de salas genéricas - exclusivas para professores"""
    id_reserva_generica = models.AutoField(primary_key=True)
    professor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas_salas_genericas')
    sala = models.ForeignKey(SalaGenérica, on_delete=models.CASCADE, related_name='reservas')
    data = models.DateField()
    horario = models.TimeField()
    motivo = models.TextField(help_text="Motivo/descrição da reserva")
    numero_alunos = models.IntegerField(default=1, help_text="Número estimado de alunos")
    
    PRESENCA_CHOICES = [
        ('pendente', 'Pendente'),
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
    ]
    presenca = models.CharField(max_length=10, choices=PRESENCA_CHOICES, default='pendente')
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data', '-horario']
        unique_together = ['sala', 'data', 'horario']
        verbose_name = "Reserva de Sala Genérica"
        verbose_name_plural = "Reservas de Salas Genéricas"

    def __str__(self):
        return f"Reserva {self.sala.nome} - {self.data} {self.horario}"
