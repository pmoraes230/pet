from django.db import models


class Consulta(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    tipo_de_consulta = models.CharField(db_column='TIPO_DE_CONSULTA', max_length=45)  # Field name made lowercase.
    retorno_agendado = models.DateField(db_column='RETORNO_AGENDADO')  # Field name made lowercase.
    tratamento = models.CharField(db_column='TRATAMENTO', max_length=100)  # Field name made lowercase.
    data_consulta = models.DateField(db_column='DATA_CONSULTA')  # Field name made lowercase.
    horario_consulta = models.TimeField(db_column='HORARIO_CONSULTA')  # Field name made lowercase.
    observacoes = models.CharField(db_column='OBSERVACOES', max_length=45)  # Field name made lowercase.
    id_pet = models.ForeignKey('Pet', models.DO_NOTHING, db_column='ID_PET')  # Field name made lowercase.
    id_veterinario = models.ForeignKey('Veterinario', models.DO_NOTHING, db_column='ID_VETERINARIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'consulta'


class ContatoTutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_tutor = models.ForeignKey('tutor', models.DO_NOTHING, db_column='ID_TUTOR', blank=True, null=True)  # Field name made lowercase.
    tipo_contato = models.CharField(db_column='TIPO_CONTATO', max_length=16)  # Field name made lowercase.
    ddd = models.CharField(db_column='DDD', max_length=2)  # Field name made lowercase.
    numero = models.CharField(db_column='NUMERO', max_length=9)  # Field name made lowercase.
    data_cadastro = models.DateTimeField(db_column='DATA_CADASTRO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contato_tutor'
        unique_together = (('id_tutor', 'ddd', 'numero'),)

class Feedback(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    feedback_app = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback'


class FeedbackPet(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    feedback_pet = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback_pet'


class PessoaFisica(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    cpf = models.IntegerField(db_column='CPF', unique=True)  # Field name made lowercase.
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')  # Field name made lowercase.
    genero = models.CharField(db_column='GENERO', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pessoa fisica'


class PessoaJuridica(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    cnpj = models.IntegerField(db_column='CNPJ', unique=True)  # Field name made lowercase.
    nome_fantasia = models.CharField(db_column='NOME_FANTASIA', max_length=45)  # Field name made lowercase.
    endereco = models.CharField(db_column='ENDERECO', max_length=45)  # Field name made lowercase.
    data_criacao = models.DateField(db_column='DATA_CRIACAO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pessoa juridica'


class Pet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='NOME', max_length=45)  # Field name made lowercase.
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')  # Field name made lowercase.
    especie = models.CharField(db_column='ESPECIE', max_length=45)  # Field name made lowercase.
    raca = models.CharField(max_length=45)
    sexo = models.CharField(db_column='SEXO', max_length=5)  # Field name made lowercase.
    pelagem = models.CharField(db_column='PELAGEM', max_length=45)  # Field name made lowercase.
    castrado = models.CharField(db_column='CASTRADO', max_length=3)  # Field name made lowercase.
    id_tutor = models.ForeignKey('Tutor', models.DO_NOTHING, db_column='ID_TUTOR')  # Field name made lowercase.
    id_consulta = models.ForeignKey('ProntuarioPet', models.DO_NOTHING, db_column='ID_CONSULTA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pet'


class ProntuarioPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    historico_veterinario = models.CharField(db_column='HISTORICO_VETERINARIO', unique=True, max_length=150)  # Field name made lowercase.
    motivo_consulta = models.TextField(db_column='MOTIVO_CONSULTA')  # Field name made lowercase.
    avaliacao_geral = models.TextField(db_column='AVALIACAO_GERAL')  # Field name made lowercase.
    procedimentos = models.TextField(db_column='PROCEDIMENTOS')  # Field name made lowercase.
    diagnostico_conslusivo = models.TextField(db_column='DIAGNOSTICO_CONSLUSIVO')  # Field name made lowercase.
    observacao = models.TextField(db_column='OBSERVACAO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'prontuario_pet'


class Tutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nome_tutor = models.CharField(max_length=80, blank=True, null=True)
    cpf = models.CharField(db_column='CPF', unique=True, max_length=14, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(max_length=80, blank=True, null=True)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)  # Field name made lowercase.
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')  # Field name made lowercase.
    id_feedback_sistema = models.ForeignKey(Feedback, models.DO_NOTHING, db_column='ID_FEEDBACK_SISTEMA', blank=True, null=True)  # Field name made lowercase.
    id_feedback_pet = models.ForeignKey(FeedbackPet, models.DO_NOTHING, db_column='ID_FEEDBACK_PET', blank=True, null=True)  # Field name made lowercase.
    senha_tutor = models.CharField(max_length=150)
    imagem_perfil_tutor = models.ImageField(upload_to='tutor')
    status_conta = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'tutor'


class Veterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='NOME', max_length=45)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=45)  # Field name made lowercase.
    crmv = models.IntegerField(db_column='CRMV', unique=True)  # Field name made lowercase.
    uf_crmv = models.CharField(db_column='UF_CRMV', max_length=5)  # Field name made lowercase.
    telefone = models.IntegerField(db_column='TELEFONE')  # Field name made lowercase.
    pessoa_juridica_idpessoa_juridica = models.ForeignKey(PessoaJuridica, models.DO_NOTHING, db_column='PESSOA JURIDICA_idPESSOA JURIDICA')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    pessoa_fisica_idpessoa_fisica = models.ForeignKey(PessoaFisica, models.DO_NOTHING, db_column='PESSOA FISICA_idPESSOA FISICA')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    senha_veterinario = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'veterinario'
