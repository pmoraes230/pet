from django.db import models


class PessoaFisica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cpf = models.CharField(db_column='CPF', max_length=14, unique=True, blank=True, null=True)
    data_nascimento = models.DateField(db_column='DATA_NASCIMENTO', blank=True, null=True)
    genero = models.CharField(db_column='GENERO', max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pessoa_fisica'

    def __str__(self):
        return self.cpf or str(self.id)


class PessoaJuridica(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    cnpj = models.CharField(db_column='CNPJ', max_length=14, unique=True, blank=True, null=True)
    nome_fantasia = models.CharField(db_column='NOME_FANTASIA', max_length=45, blank=True, null=True)
    endereco = models.CharField(db_column='ENDERECO', max_length=100, blank=True, null=True)
    data_criacao = models.DateField(db_column='DATA_CRIACAO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pessoa_juridica'

    def __str__(self):
        return self.nome_fantasia or self.cnpj or str(self.id)


class Feedback(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    feedback_app = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback'

    def __str__(self):
        return f"Feedback App {self.id}"


class FeedbackPet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    feedback_pet = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback_pet'

    def __str__(self):
        return f"Feedback Pet {self.id}"


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

    def __str__(self):
        return self.nome_tutor or self.email or str(self.id)


class Veterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=45, blank=True, null=True)
    email = models.CharField(db_column='EMAIL', max_length=45, unique=True, blank=True, null=True)
    crmv = models.IntegerField(db_column='CRMV', unique=True, blank=True, null=True)
    uf_crmv = models.CharField(db_column='UF_CRMV', max_length=5, blank=True, null=True)
    telefone = models.CharField(db_column='TELEFONE', max_length=15, blank=True, null=True)
    senha_veterinario = models.CharField(db_column='senha_veterinario', max_length=150, blank=True, null=True)
    imagem_perfil_veterinario = models.ImageField(db_column='imagem_perfil_veterinario', upload_to='veterinario/', blank=True, null=True)
    pessoa_fisica = models.ForeignKey(PessoaFisica, models.DO_NOTHING, db_column='pessoa_fisica_id', blank=True, null=True)
    pessoa_juridica = models.ForeignKey(PessoaJuridica, models.DO_NOTHING, db_column='pessoa_juridica_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veterinario'

    def __str__(self):
        return self.nome or self.email or str(self.id)


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
    personalidade = models.TextField(db_column='PERSONALIDADE', blank=True, null=True)
    imagem = models.ImageField(db_column='IMAGEM', upload_to='pets/', blank=True, null=True)
    tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='ID_TUTOR')

    class Meta:
        managed = False
        db_table = 'pet'

    def __str__(self):
        return self.nome


class Prontuariopet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    historico_veterinario = models.CharField(db_column='HISTORICO_VETERINARIO', max_length=255, blank=True, null=True)
    motivo_consulta = models.TextField(db_column='MOTIVO_CONSULTA', blank=True, null=True)
    avaliacao_geral = models.TextField(db_column='AVALIACAO_GERAL', blank=True, null=True)
    procedimentos = models.TextField(db_column='PROCEDIMENTOS', blank=True, null=True)
    diagnostico_conslusivo = models.TextField(db_column='DIAGNOSTICO_CONSLUSIVO', blank=True, null=True)
    observacao = models.TextField(db_column='OBSERVACAO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prontuariopet'

    def __str__(self):
        return f"Prontuário {self.id}"


class Consulta(models.Model):
    STATUS_CHOICES = [
        ('Agendado', 'Agendado'),
        ('Confirmado', 'Confirmado'),
        ('Concluido', 'Concluído'),
        ('Cancelado', 'Cancelado'),
    ]

    id = models.AutoField(db_column='ID', primary_key=True)
    tipo_de_consulta = models.CharField(db_column='TIPO_DE_CONSULTA', max_length=45, blank=True, null=True)
    retorno_agendado = models.DateField(db_column='RETORNO_AGENDADO', blank=True, null=True)
    tratamento = models.CharField(db_column='TRATAMENTO', max_length=100, blank=True, null=True)
    data_consulta = models.DateField(db_column='DATA_CONSULTA', blank=True, null=True)
    horario_consulta = models.TimeField(db_column='HORARIO_CONSULTA', blank=True, null=True)
    observacoes = models.CharField(db_column='OBSERVACOES', max_length=255, blank=True, null=True)
    valor_consulta = models.DecimalField(db_column='VALOR_CONSULTA', max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    status = models.CharField(db_column='STATUS', max_length=20, choices=STATUS_CHOICES, default='Agendado', blank=True, null=True)

    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET', blank=True, null=True)
    veterinario = models.ForeignKey(Veterinario, models.DO_NOTHING, db_column='ID_VETERINARIO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consulta'

    def __str__(self):
        return f"Consulta {self.id} - {self.pet} ({self.data_consulta})"


class Vacina(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=100, blank=True, null=True)
    data_aplicacao = models.DateField(db_column='DATA_APLICACAO', blank=True, null=True)
    proxima_dose = models.DateField(db_column='PROXIMA_DOSE', blank=True, null=True)
    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vacina'

    def __str__(self):
        return f"{self.nome} - {self.pet}"


class Medicamento(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    nome = models.CharField(db_column='NOME', max_length=100, blank=True, null=True)
    horario = models.TimeField(db_column='HORARIO', blank=True, null=True)
    data_inicio = models.DateField(db_column='DATA_INICIO', blank=True, null=True)
    data_fim = models.DateField(db_column='DATA_FIM', blank=True, null=True)
    observacoes = models.TextField(db_column='OBSERVACOES', blank=True, null=True)
    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'medicamento'

    def __str__(self):
        return f"{self.nome} - {self.pet}"


class ContatoVeterinario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    veterinario = models.ForeignKey(Veterinario, models.DO_NOTHING, db_column='ID_VETERINARIO')
    tipo_contato = models.CharField(db_column='TIPO_CONTATO', max_length=16, blank=True, null=True)
    ddd = models.CharField(db_column='DDD', max_length=2, blank=True, null=True)
    numero = models.CharField(db_column='NUMERO', max_length=9, blank=True, null=True)
    data_cadastro = models.DateTimeField(db_column='DATA_CADASTRO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contato_veterinario'

    def __str__(self):
        return f"{self.tipo_contato} {self.ddd}{self.numero} - {self.veterinario}"


class DiarioEmocional(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    pet = models.ForeignKey(Pet, models.DO_NOTHING, db_column='ID_PET')
    humor = models.IntegerField(db_column='HUMOR', blank=True, null=True)
    relato = models.TextField(db_column='RELATO', blank=True, null=True)
    data_registro = models.DateTimeField(db_column='DATA_REGISTRO', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diario_emocional'

    def __str__(self):
        return f"Diário {self.pet} - {self.data_registro}"

class Notificacao(models.Model):
    # Relaciona com o veterinário. Se for para tutor também, pode usar GenericForeignKey ou dois campos.
    veterinario = models.ForeignKey('Veterinario', on_delete=models.CASCADE, related_name='notificacoes', null=True, blank=True)
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_criacao']        

from django.db import models

class Mensagem(models.Model):
    # Quem envia pode ser o tutor ou o vet. Usamos IDs das suas tabelas.
    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE)
    veterinario = models.ForeignKey('Veterinario', on_delete=models.CASCADE)
    conteudo = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    enviado_por_tutor = models.BooleanField(default=True) # True se tutor enviou, False se vet enviou

    class Meta:
        db_table = 'mensagens'
        ordering = ['data_envio']        