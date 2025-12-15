from django.db import models
from datetime import date

# 1. Classes Independentes (ou dependências básicas)

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

class PessoaFisica(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    cpf = models.IntegerField(db_column='CPF', unique=True)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    genero = models.CharField(db_column='GENERO', max_length=45)

    class Meta:
        managed = False
        db_table = 'pessoa fisica'

class PessoaJuridica(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    cnpj = models.IntegerField(db_column='CNPJ', unique=True)
    nome_fantasia = models.CharField(db_column='NOME_FANTASIA', max_length=45)
    endereco = models.CharField(db_column='ENDERECO', max_length=45)
    data_criacao = models.DateField(db_column='DATA_CRIACAO')

    class Meta:
        managed = False
        db_table = 'pessoa juridica'

# 2. ProntuarioPet (Deve vir ANTES de Pet)
class ProntuarioPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    
    # Nomes exatos conforme sua imagem
    historico_veterinario = models.CharField(db_column='historico_veterinario', unique=True, max_length=150)
    motivo_consulta = models.TextField(db_column='motivo_consulta')
    avaliacao_geral = models.TextField(db_column='avaliacao_geral', blank=True, null=True)
    procedimentos = models.TextField(db_column='procedimentos', blank=True, null=True)
    
    # ATENÇÃO: Mantive o erro de digitação "conslusivo" aqui pois é assim que está no seu banco
    diagnostico_conslusivo = models.TextField(db_column='diagnostico_conslusivo', blank=True, null=True)
    
    observacao = models.TextField(db_column='observacao', blank=True, null=True)

    class Meta:
        managed = False
        # O ERRO ESTAVA AQUI: O nome real no banco é tudo junto
        db_table = 'prontuariopet'
        db_table = 'prontuariopet'  # <--- TEM QUE SER TUDO JUNTO, SEM "_"

# 3. Tutor (Deve vir ANTES de Pet e ContatoTutor)
class Tutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome_tutor = models.CharField(max_length=80, blank=True, null=True)
    cpf = models.CharField(db_column='CPF', unique=True, max_length=14, blank=True, null=True)
    email = models.CharField(db_column='EMAIL', unique=True, max_length=80, blank=True, null=True)
    endereco = models.CharField(db_column='ENDERECO', max_length=100)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    id_feedback_sistema = models.ForeignKey(Feedback, models.DO_NOTHING, db_column='ID_FEEDBACK_SISTEMA', blank=True, null=True)
    id_feedback_pet = models.ForeignKey(FeedbackPet, models.DO_NOTHING, db_column='ID_FEEDBACK_PET', blank=True, null=True)
    senha_tutor = models.CharField(max_length=150)
    imagem_perfil_tutor = models.ImageField(upload_to='tutor', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor'

class ContatoTutor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    id_tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='ID_TUTOR', blank=True, null=True)
    tipo_contato = models.CharField(db_column='TIPO_CONTATO', max_length=16)
    ddd = models.CharField(db_column='DDD', max_length=2)
    numero = models.CharField(db_column='NUMERO', max_length=9)
    data_cadastro = models.DateTimeField(db_column='DATA_CADASTRO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contato_tutor'
        unique_together = (('id_tutor', 'ddd', 'numero'),)

# 4. Pet (Agora pode referenciar Tutor e ProntuarioPet sem erro)
class Pet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO')
    especie = models.CharField(db_column='ESPECIE', max_length=45)
    raca = models.CharField(max_length=45)
    sexo = models.CharField(db_column='SEXO', max_length=5)
    pelagem = models.CharField(db_column='PELAGEM', max_length=45)
    castrado = models.CharField(db_column='CASTRADO', max_length=3)
    
    # FKs
    id_tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='ID_TUTOR')
    # Atenção: Referenciando a classe ProntuarioPet diretamente (sem aspas, pois ela já foi lida acima)
    id_consulta = models.ForeignKey(ProntuarioPet, models.DO_NOTHING, db_column='ID_CONSULTA') 

    class Meta:
        managed = False
        db_table = 'pet'

    @property
    def idade(self):
        if not self.data_nascimento:
            return 0
        today = date.today()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))

# 5. Veterinário e Consulta (Dependem de Pet)

class Veterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45)
    email = models.CharField(db_column='EMAIL', max_length=45)
    crmv = models.IntegerField(db_column='CRMV', unique=True)
    uf_crmv = models.CharField(db_column='UF_CRMV', max_length=5)
    telefone = models.IntegerField(db_column='TELEFONE')
    pessoa_juridica_idpessoa_juridica = models.ForeignKey(PessoaJuridica, models.DO_NOTHING, db_column='PESSOA JURIDICA_idPESSOA JURIDICA', null=True)
    pessoa_fisica_idpessoa_fisica = models.ForeignKey(PessoaFisica, models.DO_NOTHING, db_column='PESSOA FISICA_idPESSOA FISICA', null=True)
    senha_veterinario = models.CharField(max_length=150)
    imagem_perfil_veterinario = models.ImageField(upload_to='veterinario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veterinario'

class ContatoVeterinario(models.Model):
    id = models.AutoField(primary_key=True)
    id_veterinario = models.ForeignKey(Veterinario, models.DO_NOTHING, db_column='ID_VETERINARIO')
    tipo_contato = models.CharField(max_length=16)
    ddd = models.CharField(max_length=2)
    numero = models.CharField(max_length=9)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'contato_veterinario'

class Consulta(models.Model):
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
    
    valor_consulta = models.DecimalField(db_column='VALOR_CONSULTA', max_digits=10, decimal_places=2, default=0)
    status = models.CharField(db_column='STATUS', max_length=20, choices=STATUS_CHOICES, default='Agendado')

    id_pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET')
    id_veterinario = models.ForeignKey(Veterinario, models.DO_NOTHING, db_column='ID_VETERINARIO')

    class Meta:
        managed = False
        db_table = 'consulta'