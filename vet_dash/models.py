from django.db import models

class PessoaFisica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cpf = models.CharField(db_column='CPF', unique=True, max_length=14)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    genero = models.CharField(db_column='GENERO', max_length=45)

    class Meta:
        managed = False
        db_table = 'pessoa_fisica'


class PessoaJuridica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cnpj = models.CharField(db_column='CNPJ', unique=True, max_length=14)
    nome_fantasia = models.CharField(db_column='NOME_FANTASIA', max_length=45)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)
    data_criacao = models.DateField(db_column='DATA_CRIACAO')

    class Meta:
        managed = False
        db_table = 'pessoa_juridica'


class Veterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45)
    email = models.CharField(db_column='EMAIL', max_length=45, unique=True)
    crmv = models.IntegerField(db_column='CRMV', unique=True)
    uf_crmv = models.CharField(db_column='UF_CRMV', max_length=5)
    telefone = models.CharField(db_column='TELEFONE', max_length=15)
    pessoa_fisica = models.ForeignKey(
    
        'PessoaFisica',
        models.DO_NOTHING,
        db_column='pessoa_fisica_id',
        null=True,
        blank=True
    )
    imagem_perfil_veterinario = models.ImageField(upload_to='veterinario', blank=True, null=True)
    pessoa_juridica = models.ForeignKey(
        'PessoaJuridica',
        models.DO_NOTHING,
        db_column='pessoa_juridica_id',
        null=True,
        blank=True
    )
    senha_veterinario = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'veterinario'


class Tutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome_tutor = models.CharField(max_length=80, blank=True, null=True)
    cpf = models.CharField(db_column='CPF', unique=True, max_length=14, blank=True, null=True)
    email = models.CharField(db_column='EMAIL', unique=True, max_length=80, blank=True, null=True)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    senha_tutor = models.CharField(max_length=150)
    imagem_perfil_tutor = models.ImageField(upload_to='tutor', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor'


class Pet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    especie = models.CharField(db_column='ESPECIE', max_length=45)
    raca = models.CharField(max_length=45)
    sexo = models.CharField(db_column='SEXO', max_length=5)
    pelagem = models.CharField(db_column='PELAGEM', max_length=45)
    castrado = models.CharField(db_column='CASTRADO', max_length=3)
    id_tutor = models.ForeignKey('Tutor', models.DO_NOTHING, db_column='ID_TUTOR')
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    personalidade = models.CharField(max_length=255, null=True, blank=True)
    imagem = models.ImageField(upload_to='pets/', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'pet'


class ProntuarioPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    historico_veterinario = models.CharField(db_column='HISTORICO_VETERINARIO', unique=True, max_length=150)
    motivo_consulta = models.TextField(db_column='MOTIVO_CONSULTA')
    avaliacao_geral = models.TextField(db_column='AVALIACAO_GERAL')
    procedimentos = models.TextField(db_column='PROCEDIMENTOS')
    diagnostico_conslusivo = models.TextField(db_column='DIAGNOSTICO_CONSLUSIVO')
    observacao = models.TextField(db_column='OBSERVACAO')

    class Meta:
        managed = False
        db_table = 'prontuario_pet'


class Consulta(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    tipo_de_consulta = models.CharField(db_column='TIPO_DE_CONSULTA', max_length=45)
    retorno_agendado = models.DateField(db_column='RETORNO_AGENDADO')
    tratamento = models.CharField(db_column='TRATAMENTO', max_length=100)
    data_consulta = models.DateField(db_column='DATA_CONSULTA')
    horario_consulta = models.TimeField(db_column='HORARIO_CONSULTA')
    observacoes = models.CharField(db_column='OBSERVACOES', max_length=45)
    id_pet = models.ForeignKey('Pet', models.DO_NOTHING, db_column='ID_PET')
    id_veterinario = models.ForeignKey('Veterinario', models.DO_NOTHING, db_column='ID_VETERINARIO')

    class Meta:
        managed = False
        db_table = 'consulta'


class ContatoVeterinario(models.Model):
    id = models.AutoField(primary_key=True)
    id_veterinario = models.ForeignKey('Veterinario', models.DO_NOTHING, db_column='ID_VETERINARIO')
    tipo_contato = models.CharField(max_length=16)
    ddd = models.CharField(max_length=2)
    numero = models.CharField(max_length=9)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'contato_veterinario'

class Consulta(models.Model):
    # Opções de status para usar no código (opcional, ajuda na organização)
    STATUS_CHOICES = [
        ('Agendado', 'Agendado'),
        ('Confirmado', 'Confirmado'),
        ('Concluido', 'Concluído'),
        ('Cancelado', 'Cancelado'),
    ]

    id = models.AutoField(db_column='ID', primary_key=True)
    tipo_de_consulta = models.CharField(db_column='TIPO_DE_CONSULTA', max_length=45)
    retorno_agendado = models.DateField(db_column='RETORNO_AGENDADO', blank=True, null=True)
    tratamento = models.CharField(db_column='TRATAMENTO', max_length=100, blank=True, null=True)
    data_consulta = models.DateField(db_column='DATA_CONSULTA')
    horario_consulta = models.TimeField(db_column='HORARIO_CONSULTA')
    observacoes = models.TextField(db_column='OBSERVACOES', blank=True, null=True)
    
    # NOVOS CAMPOS
    valor_consulta = models.DecimalField(db_column='VALOR_CONSULTA', max_digits=10, decimal_places=2, default=0)
    status = models.CharField(db_column='STATUS', max_length=20, choices=STATUS_CHOICES, default='Agendado')

    id_pet = models.ForeignKey('Pet', models.DO_NOTHING, db_column='ID_PET')
    id_veterinario = models.ForeignKey('Veterinario', models.DO_NOTHING, db_column='ID_VETERINARIO')

    class Meta:
        managed = False
        db_table = 'consulta'

        
class ProntuarioPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    historico_veterinario = models.CharField(db_column='HISTORICO_VETERINARIO', max_length=150, blank=True, null=True)
    motivo_consulta = models.TextField(db_column='MOTIVO_CONSULTA', blank=True, null=True)
    avaliacao_geral = models.TextField(db_column='AVALIACAO_GERAL', blank=True, null=True)
    procedimentos = models.TextField(db_column='PROCEDIMENTOS', blank=True, null=True)
    diagnostico_conslusivo = models.TextField(db_column='DIAGNOSTICO_CONSLUSIVO', blank=True, null=True)
    observacao = models.TextField(db_column='OBSERVACAO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prontuariopet' # Certifique-se que está IGUAL ao nome no MySQL        

class Vacina(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=100)
    data_aplicacao = models.DateField(db_column='DATA_APLICACAO')
    proxima_dose = models.DateField(db_column='PROXIMA_DOSE', blank=True, null=True)
    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET')
    
    class Meta:
        managed = False
        db_table = 'vacina'        