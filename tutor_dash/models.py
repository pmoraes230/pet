from django.db import models

# 1. PESSOAS E IDENTIFICAÇÃO
class PessoaFisica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cpf = models.CharField(db_column='CPF', max_length=14, unique=True)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    genero = models.CharField(db_column='GENERO', max_length=45)
    class Meta:
        managed = False
        db_table = 'pessoa_fisica'

class PessoaJuridica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cnpj = models.CharField(db_column='CNPJ', max_length=14, unique=True)
    nome_fantasia = models.CharField(db_column='NOME_FANTASIA', max_length=45)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)
    data_criacao = models.DateField(db_column='DATA_CRIACAO')
    class Meta:
        managed = False
        db_table = 'pessoa_juridica'

# 2. FEEDBACKS
class Feedback(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    feedback_app = models.TextField(db_column='feedback_app', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'feedback'

class FeedbackPet(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    feedback_pet = models.TextField(db_column='feedback_pet', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'feedback_pet'

# 3. TUTOR E CONTATOS
class Tutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome_tutor = models.CharField(db_column='nome_tutor', max_length=80, blank=True, null=True)
    cpf = models.CharField(db_column='CPF', max_length=14, unique=True, blank=True, null=True)
    email = models.CharField(db_column='EMAIL', max_length=80, unique=True, blank=True, null=True)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    senha_tutor = models.CharField(db_column='senha_tutor', max_length=150)
    imagem_perfil_tutor = models.ImageField(db_column='imagem_perfil_tutor', upload_to='tutor', blank=True, null=True)
    id_feedback_sistema = models.ForeignKey(Feedback, models.DO_NOTHING, db_column='ID_FEEDBACK_SISTEMA', blank=True, null=True)
    id_feedback_pet = models.ForeignKey(FeedbackPet, models.DO_NOTHING, db_column='ID_FEEDBACK_PET', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'tutor'

class ContatoTutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='ID_TUTOR')
    tipo_contato = models.CharField(max_length=16)
    ddd = models.CharField(max_length=2)
    numero = models.CharField(max_length=9)
    class Meta:
        managed = False
        db_table = 'contato_tutor'

# 4. VETERINÁRIO E CONTATOS
class Veterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45)
    email = models.CharField(db_column='EMAIL', max_length=45, unique=True)
    crmv = models.IntegerField(db_column='CRMV', unique=True)
    uf_crmv = models.CharField(db_column='UF_CRMV', max_length=5)
    telefone = models.CharField(db_column='TELEFONE', max_length=15)
    senha_veterinario = models.CharField(db_column='senha_veterinario', max_length=150)
    imagem_perfil_veterinario = models.ImageField(upload_to='veterinario', blank=True, null=True)
    pessoa_fisica = models.ForeignKey(PessoaFisica, models.DO_NOTHING, db_column='pessoa_fisica_id', blank=True, null=True)
    pessoa_juridica = models.ForeignKey(PessoaJuridica, models.DO_NOTHING, db_column='pessoa_juridica_id', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'veterinario'

class ContatoVeterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    veterinario = models.ForeignKey(Veterinario, models.DO_NOTHING, db_column='ID_VETERINARIO')
    tipo_contato = models.CharField(db_column='TIPO_CONTATO', max_length=16)
    ddd = models.CharField(db_column='DDD', max_length=2)
    numero = models.CharField(db_column='NUMERO', max_length=9)
    data_cadastro = models.DateTimeField(db_column='DATA_CADASTRO', auto_now_add=True)
    class Meta:
        managed = False
        db_table = 'contato_veterinario'

# 5. PET E SAÚDE
class ProntuarioPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    historico_veterinario = models.CharField(db_column='HISTORICO_VETERINARIO', max_length=255)
    motivo_consulta = models.TextField(db_column='MOTIVO_CONSULTA')
    avaliacao_geral = models.TextField(db_column='AVALIACAO_GERAL', blank=True, null=True)
    procedimentos = models.TextField(db_column='PROCEDIMENTOS', blank=True, null=True)
    diagnostico_conslusivo = models.TextField(db_column='DIAGNOSTICO_CONSLUSIVO', blank=True, null=True)
    observacao = models.TextField(db_column='OBSERVACAO', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'prontuariopet'

class Pet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    especie = models.CharField(db_column='ESPECIE', max_length=45)
    raca = models.CharField(db_column='RACA', max_length=45)
    sexo = models.CharField(db_column='SEXO', max_length=5)
    pelagem = models.CharField(db_column='PELAGEM', max_length=45)
    castrado = models.CharField(db_column='CASTRADO', max_length=3)
    peso = models.CharField(db_column='PESO', max_length=10, blank=True, null=True)
    descricao = models.TextField(db_column='DESCRICAO', blank=True, null=True)
    imagem = models.ImageField(db_column='IMAGEM', upload_to='pets/', blank=True, null=True)
    personalidade = models.TextField(db_column='PERSONALIDADE', blank=True, null=True)
    tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='ID_TUTOR')
    class Meta:
        managed = False
        db_table = 'pet'

# 6. CONSULTAS, VACINAS E DIÁRIO
class Consulta(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tipo_de_consulta = models.CharField(db_column='TIPO_DE_CONSULTA', max_length=45)
    retorno_agendado = models.DateField(db_column='RETORNO_AGENDADO', blank=True, null=True)
    tratamento = models.CharField(db_column='TRATAMENTO', max_length=100, blank=True, null=True)
    data_consulta = models.DateField(db_column='DATA_CONSULTA')
    horario_consulta = models.TimeField(db_column='HORARIO_CONSULTA')
    observacoes = models.CharField(db_column='OBSERVACOES', max_length=255, blank=True, null=True)
    valor_consulta = models.DecimalField(db_column='VALOR_CONSULTA', max_digits=10, decimal_places=2, default=0)
    status = models.CharField(db_column='STATUS', max_length=20, default='Agendado')
    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET')
    veterinario = models.ForeignKey(Veterinario, models.DO_NOTHING, db_column='ID_VETERINARIO')
    class Meta:
        managed = False
        db_table = 'consulta'

class Vacina(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=100)
    data_aplicacao = models.DateField(db_column='DATA_APLICACAO')
    proxima_dose = models.DateField(db_column='PROXIMA_DOSE', blank=True, null=True)
    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET')
    class Meta:
        managed = False
        db_table = 'vacina'

class DiarioEmocional(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET')
    humor = models.IntegerField(db_column='HUMOR')
    relato = models.TextField(db_column='RELATO')
    data_registro = models.DateTimeField(db_column='DATA_REGISTRO', auto_now_add=True)
    class Meta:
        managed = False
        db_table = 'diario_emocional'


        