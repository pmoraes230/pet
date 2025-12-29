from django.db import models
from datetime import date

# ===============================
# FEEDBACK
# ===============================

class Feedback(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    feedback_app = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback'


class FeedbackPet(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    feedback_pet = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback_pet'


# ===============================
# PRONTUÁRIO
# ===============================

class ProntuarioPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    historico_veterinario = models.CharField(max_length=150)
    motivo_consulta = models.TextField()
    avaliacao_geral = models.TextField(blank=True, null=True)
    procedimentos = models.TextField(blank=True, null=True)
    diagnostico_conslusivo = models.TextField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prontuariopet'


# ===============================
# TUTOR
# ===============================

class Tutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome_tutor = models.CharField(max_length=80, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    email = models.CharField(max_length=80, unique=True, blank=True, null=True)
    endereco = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    senha_tutor = models.CharField(max_length=150)
    imagem_perfil_tutor = models.ImageField(upload_to='tutor', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor'


class ContatoTutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tutor = models.ForeignKey(
        Tutor,
        models.DO_NOTHING,
        db_column='ID_TUTOR'
    )
    tipo_contato = models.CharField(max_length=16)
    ddd = models.CharField(max_length=2)
    numero = models.CharField(max_length=9)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contato_tutor'




# ===============================
# PET
# ===============================

class Pet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    # Adicionamos db_column para o Django saber que no SQL o nome é MAIÚSCULO
    nome = models.CharField(max_length=45, db_column='NOME')
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    especie = models.CharField(max_length=45, db_column='ESPECIE')
    raca = models.CharField(max_length=45, db_column='RACA')
    sexo = models.CharField(max_length=5, db_column='SEXO')
    pelagem = models.CharField(max_length=45, db_column='PELAGEM')
    castrado = models.CharField(max_length=3, db_column='CASTRADO')
    
    # Novos campos que você adicionou
    peso = models.CharField(max_length=10, db_column='PESO', blank=True, null=True)
    descricao = models.TextField(db_column='DESCRICAO', blank=True, null=True)
    imagem = models.ImageField(upload_to='pets/', db_column='IMAGEM', blank=True, null=True)
    personalidade = models.TextField(db_column='PERSONALIDADE', blank=True, null=True)

    tutor = models.ForeignKey(
        Tutor,
        models.DO_NOTHING,
        db_column='ID_TUTOR'
    )

    class Meta:
        managed = False
        db_table = 'pet'


# ===============================
# CONSULTA
# ===============================

class Consulta(models.Model):
    STATUS_CHOICES = [
        ('Agendado', 'Agendado'),
        ('Confirmado', 'Confirmado'),
        ('Concluido', 'Concluído'),
        ('Cancelado', 'Cancelado'),
    ]

    id = models.AutoField(db_column='ID', primary_key=True)
    tipo_de_consulta = models.CharField(max_length=45)
    retorno_agendado = models.DateField(blank=True, null=True)
    tratamento = models.CharField(max_length=100, blank=True, null=True)
    data_consulta = models.DateField()
    horario_consulta = models.TimeField()
    observacoes = models.TextField(blank=True, null=True)
    valor_consulta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Agendado')

    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET')
    veterinario = models.ForeignKey('Veterinario', models.DO_NOTHING, db_column='ID_VETERINARIO')

    class Meta:
        managed = False
        db_table = 'consulta'


# ===============================
# VETERINÁRIO
# ===============================

class Veterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    crmv = models.IntegerField(unique=True)
    uf_crmv = models.CharField(max_length=5)
    telefone = models.IntegerField()
    senha_veterinario = models.CharField(max_length=150)
    imagem_perfil_veterinario = models.ImageField(upload_to='veterinario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veterinario'
