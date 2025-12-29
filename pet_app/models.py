from django.db import models

# =====================================================
# PESSOA FÍSICA
# =====================================================
class PessoaFisica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cpf = models.CharField(db_column='CPF', max_length=14, unique=True)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    genero = models.CharField(db_column='GENERO', max_length=45)

    class Meta:
        managed = False
        db_table = 'pessoa_fisica'


# =====================================================
# PESSOA JURÍDICA
# =====================================================
class PessoaJuridica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cnpj = models.CharField(db_column='CNPJ', max_length=14, unique=True)
    nome_fantasia = models.CharField(db_column='NOME_FANTASIA', max_length=45)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)
    data_criacao = models.DateField(db_column='DATA_CRIACAO')

    class Meta:
        managed = False
        db_table = 'pessoa_juridica'


# =====================================================
# FEEDBACKS
# =====================================================
class Feedback(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    feedback_app = models.TextField(db_column='FEEDBACK_APP', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'feedback'


class FeedbackPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    feedback_pet = models.TextField(db_column='FEEDBACK_PET', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'feedback_pet'


# =====================================================
# TUTOR
# =====================================================
class Tutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome_tutor = models.CharField(db_column='NOME_TUTOR', max_length=80)
    cpf = models.CharField(db_column='CPF', max_length=14, unique=True)
    email = models.CharField(db_column='EMAIL', max_length=80, unique=True)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    senha_tutor = models.CharField(db_column='SENHA_TUTOR', max_length=150)
    imagem_perfil_tutor = models.CharField(
        db_column='IMAGEM_PERFIL_TUTOR',
        max_length=255,
        null=True,
        blank=True
    )
    feedback_sistema = models.ForeignKey(
        Feedback,
        models.DO_NOTHING,
        db_column='ID_FEEDBACK_SISTEMA',
        null=True,
        blank=True
    )
    feedback_pet = models.ForeignKey(
        FeedbackPet,
        models.DO_NOTHING,
        db_column='ID_FEEDBACK_PET',
        null=True,
        blank=True
    )

    class Meta:
        managed = False
        db_table = 'tutor'


# =====================================================
# VETERINÁRIO
# =====================================================
class Veterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    crmv = models.IntegerField(unique=True)
    uf_crmv = models.CharField(max_length=5)
    telefone = models.CharField(max_length=15)
    senha_veterinario = models.CharField(max_length=150)

    pessoa_fisica = models.ForeignKey(
        'PessoaFisica',
        models.DO_NOTHING,
        db_column='pessoa_fisica_id',
        blank=True,
        null=True
    )

    pessoa_juridica = models.ForeignKey(
        'PessoaJuridica',
        models.DO_NOTHING,
        db_column='pessoa_juridica_id',
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'veterinario'



# =====================================================
# PRONTUÁRIO PET
# =====================================================
class ProntuarioPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    historico_veterinario = models.CharField(db_column='HISTORICO_VETERINARIO', max_length=255)
    motivo_consulta = models.TextField(db_column='MOTIVO_CONSULTA')
    avaliacao_geral = models.TextField(db_column='AVALIACAO_GERAL')
    procedimentos = models.TextField(db_column='PROCEDIMENTOS')
    diagnostico_conslusivo = models.TextField(db_column='DIAGNOSTICO_CONSLUSIVO')
    observacao = models.TextField(db_column='OBSERVACAO')

    class Meta:
        managed = False
        db_table = 'prontuariopet'


# =====================================================
# PET
# =====================================================
class Pet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    especie = models.CharField(db_column='ESPECIE', max_length=45)
    raca = models.CharField(db_column='RACA', max_length=45)
    sexo = models.CharField(db_column='SEXO', max_length=5)
    pelagem = models.CharField(db_column='PELAGEM', max_length=45)
    castrado = models.CharField(db_column='CASTRADO', max_length=3)
    tutor = models.ForeignKey(
        Tutor,
        models.DO_NOTHING,
        db_column='ID_TUTOR',
        related_name='pets'
    )

    class Meta:
        managed = False
        db_table = 'pet'


# =====================================================
# CONSULTA
# =====================================================
class Consulta(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tipo_de_consulta = models.CharField(db_column='TIPO_DE_CONSULTA', max_length=45)
    retorno_agendado = models.DateField(db_column='RETORNO_AGENDADO', null=True, blank=True)
    tratamento = models.CharField(db_column='TRATAMENTO', max_length=100, null=True, blank=True)
    data_consulta = models.DateField(db_column='DATA_CONSULTA')
    horario_consulta = models.TimeField(db_column='HORARIO_CONSULTA')
    observacoes = models.CharField(db_column='OBSERVACOES', max_length=255, null=True, blank=True)
    valor_consulta = models.DecimalField(
        db_column='VALOR_CONSULTA',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    status = models.CharField(db_column='STATUS', max_length=20, default='Agendado')
    pet = models.ForeignKey(
        Pet,
        models.DO_NOTHING,
        db_column='ID_PET',
        related_name='consultas'
    )
    veterinario = models.ForeignKey(
        Veterinario,
        models.DO_NOTHING,
        db_column='ID_VETERINARIO',
        related_name='consultas'
    )

    class Meta:
        managed = False
        db_table = 'consulta'


# =====================================================
# CONTATO VETERINÁRIO
# =====================================================
class ContatoVeterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    veterinario = models.ForeignKey(
        Veterinario,
        models.DO_NOTHING,
        db_column='ID_VETERINARIO',
        related_name='contatos'
    )
    tipo_contato = models.CharField(db_column='TIPO_CONTATO', max_length=16)
    ddd = models.CharField(db_column='DDD', max_length=2)
    numero = models.CharField(db_column='NUMERO', max_length=9)
    data_cadastro = models.DateTimeField(db_column='DATA_CADASTRO')

    class Meta:
        managed = False
        db_table = 'contato_veterinario'


# =====================================================
# CONTATO TUTOR (se existir)
# =====================================================
class ContatoTutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tutor = models.ForeignKey(
        Tutor,
        models.DO_NOTHING,
        db_column='ID_TUTOR',
        related_name='contatos'
    )
    tipo_contato = models.CharField(db_column='TIPO_CONTATO', max_length=16)
    ddd = models.CharField(db_column='DDD', max_length=2)
    numero = models.CharField(db_column='NUMERO', max_length=9)
    data_cadastro = models.DateTimeField(db_column='DATA_CADASTRO')

    class Meta:
        managed = False
        db_table = 'contato_tutor'
