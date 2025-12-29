-- ===============================
-- BANCO DE DADOS COMPLETO
-- ===============================
DROP DATABASE IF EXISTS pet_patrick_db;
CREATE DATABASE pet_patrick_db;
USE pet_patrick_db;

-- ===============================
-- TABELAS AUXILIARES
-- ===============================
CREATE TABLE pessoa_fisica (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    CPF VARCHAR(14) UNIQUE,
    DATA_NASCIMENTO DATE,
    GENERO VARCHAR(45)
);

CREATE TABLE pessoa_juridica (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    CNPJ VARCHAR(14) UNIQUE,
    NOME_FANTASIA VARCHAR(45),
    ENDERECO VARCHAR(100),
    DATA_CRIACAO DATE
);

CREATE TABLE feedback (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    feedback_app TEXT
);

CREATE TABLE feedback_pet (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    feedback_pet TEXT
);

-- ===============================
-- TUTOR
-- ===============================
CREATE TABLE tutor (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    nome_tutor VARCHAR(80),
    CPF VARCHAR(14) UNIQUE,
    EMAIL VARCHAR(80) UNIQUE,
    ENDERECO VARCHAR(100),
    DATA_NASCIMENTO DATE,
    senha_tutor VARCHAR(150),
    imagem_perfil_tutor VARCHAR(255),
    ID_FEEDBACK_SISTEMA INT,
    ID_FEEDBACK_PET INT,
    FOREIGN KEY (ID_FEEDBACK_SISTEMA) REFERENCES feedback(ID),
    FOREIGN KEY (ID_FEEDBACK_PET) REFERENCES feedback_pet(ID)
);

-- ===============================
-- PROCEDURE TUTOR
-- ===============================
DROP PROCEDURE IF EXISTS insert_tutor;
DELIMITER $$
CREATE PROCEDURE insert_tutor (
    IN p_nome_tutor VARCHAR(80),
    IN p_cpf VARCHAR(14),
    IN p_email VARCHAR(80),
    IN p_endereco VARCHAR(100),
    IN p_data_nascimento DATE,
    IN p_senha_tutor VARCHAR(150)
)
BEGIN
    IF p_nome_tutor IS NULL OR TRIM(p_nome_tutor) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O nome do tutor é obrigatório';
    END IF;

    IF p_cpf IS NULL OR p_cpf NOT REGEXP '^[0-9]{11}$' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CPF inválido';
    END IF;

    IF EXISTS (SELECT 1 FROM tutor WHERE EMAIL = p_email) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Email já cadastrado';
    END IF;

    IF EXISTS (SELECT 1 FROM tutor WHERE CPF = p_cpf) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CPF já cadastrado';
    END IF;

    INSERT INTO tutor (
        nome_tutor, CPF, EMAIL, ENDERECO, DATA_NASCIMENTO, senha_tutor
    )
    VALUES (
        p_nome_tutor, p_cpf, p_email, p_endereco, p_data_nascimento, p_senha_tutor
    );
END $$
DELIMITER ;

-- ===============================
-- VETERINÁRIO
-- ===============================
CREATE TABLE veterinario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(45),
    EMAIL VARCHAR(45) UNIQUE,
    CRMV INT UNIQUE,
    UF_CRMV VARCHAR(5),
    TELEFONE VARCHAR(15),
    pessoa_fisica_id INT NULL,
    pessoa_juridica_id INT NULL,
    senha_veterinario VARCHAR(150),
    FOREIGN KEY (pessoa_fisica_id) REFERENCES pessoa_fisica(ID),
    FOREIGN KEY (pessoa_juridica_id) REFERENCES pessoa_juridica(ID)
);

-- ===============================
-- PRONTUÁRIO PET
-- ===============================
CREATE TABLE prontuariopet (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    HISTORICO_VETERINARIO VARCHAR(255),
    MOTIVO_CONSULTA TEXT,
    AVALIACAO_GERAL TEXT,
    PROCEDIMENTOS TEXT,
    DIAGNOSTICO_CONSLUSIVO TEXT,
    OBSERVACAO TEXT
);

-- ===============================
-- PET
-- ===============================
CREATE TABLE pet (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(45),
    DATA_NASCIMENTO DATE,
    ESPECIE VARCHAR(45),
    RACA VARCHAR(45),
    SEXO VARCHAR(5),
    PELAGEM VARCHAR(45),
    CASTRADO VARCHAR(3),
    ID_TUTOR INT,
    PESO VARCHAR(10),
    DESCRICAO TEXT,
    IMAGEM VARCHAR(255),
    PERSONALIDADE TEXT,
    FOREIGN KEY (ID_TUTOR) REFERENCES tutor(ID)
);

-- ===============================
-- PROCEDURE PET
-- ===============================
DROP PROCEDURE IF EXISTS insert_pet;
DELIMITER $$
CREATE PROCEDURE insert_pet (
    IN p_nome VARCHAR(45),
    IN p_data_nascimento DATE,
    IN p_especie VARCHAR(45),
    IN p_raca VARCHAR(45),
    IN p_sexo VARCHAR(5),
    IN p_pelagem VARCHAR(45),
    IN p_castrado VARCHAR(3),
    IN p_id_tutor INT
)
BEGIN
    -- VALIDAÇÕES
    IF p_nome IS NULL OR TRIM(p_nome) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O nome do pet é obrigatório';
    END IF;

    IF p_especie IS NULL OR TRIM(p_especie) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A espécie do pet é obrigatória';
    END IF;

    IF p_sexo IS NULL OR TRIM(p_sexo) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O sexo do pet é obrigatório';
    END IF;

    IF p_castrado IS NULL OR TRIM(p_castrado) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Informe se o pet é castrado';
    END IF;

    IF p_id_tutor IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O tutor é obrigatório';
    END IF;

    -- VALIDAÇÃO DE CHAVE ESTRANGEIRA
    IF NOT EXISTS (SELECT 1 FROM tutor WHERE ID = p_id_tutor) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tutor informado não existe';
    END IF;

    -- INSERÇÃO
    INSERT INTO pet (
        NOME, DATA_NASCIMENTO, ESPECIE, RACA, SEXO, PELAGEM, CASTRADO, ID_TUTOR
    )
    VALUES (
        p_nome, p_data_nascimento, p_especie, p_raca, p_sexo, p_pelagem, p_castrado, p_id_tutor
    );
END $$
DELIMITER ;

-- ===============================
-- CONSULTA
-- ===============================
CREATE TABLE consulta (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    TIPO_DE_CONSULTA VARCHAR(45),
    RETORNO_AGENDADO DATE,
    TRATAMENTO VARCHAR(100),
    DATA_CONSULTA DATE,
    HORARIO_CONSULTA TIME,
    OBSERVACOES VARCHAR(255),
    VALOR_CONSULTA DECIMAL(10,2) DEFAULT 0.00,
    STATUS VARCHAR(20) DEFAULT 'Agendado',
    ID_PET INT,
    ID_VETERINARIO INT,
    FOREIGN KEY (ID_PET) REFERENCES pet(ID),
    FOREIGN KEY (ID_VETERINARIO) REFERENCES veterinario(ID)
);

-- ===============================
-- CONTATO VETERINARIO
-- ===============================
CREATE TABLE contato_veterinario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    ID_VETERINARIO INT,
    TIPO_CONTATO VARCHAR(16),
    DDD VARCHAR(2),
    NUMERO VARCHAR(9),
    DATA_CADASTRO DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_VETERINARIO) REFERENCES veterinario(ID)
);

-- ===============================
-- VACINA
-- ===============================
CREATE TABLE vacina (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(100),
    DATA_APLICACAO DATE,
    PROXIMA_DOSE DATE,
    ID_PET INT,
    FOREIGN KEY (ID_PET) REFERENCES pet(ID)
);
