create database pet_patrick_db;
  
USE pet_patrick_db;

SHOW PROCEDURE STATUS WHERE Db = 'pet_patrick_db';

DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN nome_tutor VARCHAR(255),
    IN cpf VARCHAR(14),
    IN data_nascimento DATE,
    IN endereco VARCHAR(255),
    IN email VARCHAR(255),
    IN senha_tutor VARCHAR(255)
)
BEGIN
    INSERT INTO tutor (nome_tutor, cpf, data_nascimento, endereco, email, senha_tutor)
    VALUES (nome_tutor, cpf, data_nascimento, endereco, email, senha_tutor);
END $$

DELIMITER ;

CALL insert_tutor('João Silva', '123.456.789-00', '1985-01-01', 'Rua Exemplo, 123', 'joao@email.com', 'senha123');

SHOW TABLES LIKE 'tutor';

CREATE TABLE tutor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    data_nascimento DATE NOT NULL,
    endereco VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL
);




DROP PROCEDURE IF EXISTS insert_tutor;

DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN p_nome_completo VARCHAR(100),
    IN p_cpf VARCHAR(14),
    IN p_data_nascimento DATE,
    IN p_endereco VARCHAR(255),
    IN p_email VARCHAR(100),
    IN p_senha VARCHAR(100)
)
BEGIN
    INSERT INTO tutor (nome_completo, cpf, data_nascimento, endereco, email, senha)
    VALUES (p_nome_completo, p_cpf, p_data_nascimento, p_endereco, p_email, p_senha);
END$$

DELIMITER ;

CALL insert_tutor(
    'João Silva',
    '123.456.789-00',
    '1985-01-01',
    'Rua Exemplo, 123',
    'joao@email.com',
    'senha123'
);
SELECT * FROM tutor;
DROP PROCEDURE IF EXISTS insert_tutor;

-- Excluir a tabela antiga se existir
DROP TABLE IF EXISTS tutor;

-- Criar a tabela nova
CREATE TABLE tutor (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    nome_tutor VARCHAR(80),
    cpf VARCHAR(14) UNIQUE,
    email VARCHAR(80),
    endereco VARCHAR(100),
    data_nascimento DATE,
    senha_tutor VARCHAR(150),
    imagem_perfil_tutor VARCHAR(255),
    ID_FEEDBACK_SISTEMA INT,
    ID_FEEDBACK_PET INT,
    FOREIGN KEY (ID_FEEDBACK_SISTEMA) REFERENCES feedback(ID),
    FOREIGN KEY (ID_FEEDBACK_PET) REFERENCES feedback_pet(ID)
);


-- Criar a tabela feedback
CREATE TABLE feedback (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    feedback_app TEXT
);

-- Criar a tabela feedback_pet
CREATE TABLE feedback_pet (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    feedback_pet TEXT
);

DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN p_nome_tutor VARCHAR(80),
    IN p_cpf VARCHAR(14),
    IN p_data_nascimento DATE,
    IN p_endereco VARCHAR(100),
    IN p_email VARCHAR(80),
    IN p_senha_tutor VARCHAR(150)
)
BEGIN
    INSERT INTO tutor (nome_tutor, cpf, data_nascimento, endereco, email, senha_tutor)
    VALUES (p_nome_tutor, p_cpf, p_data_nascimento, p_endereco, p_email, p_senha_tutor);
END $$

DELIMITER ;

CALL insert_tutor('João Silva', '123.456.789-00', '1985-01-01', 'Rua Exemplo, 123', 'joao@email.com', 'senha123');

CALL insert_tutor('Rayan Rodrigues Mamede De Aviz nogueira', '02162120224', '2009-06-11', 'Rua Exemplo, 123', 'rayan@gmail.com', '1234');

DROP PROCEDURE IF EXISTS insert_tutor;

DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN p_nome_completo VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_senha VARCHAR(100),
    IN p_cpf VARCHAR(14),
    IN p_data_nascimento DATE
)
BEGIN
    INSERT INTO tutor (nome_tutor, email, senha_tutor, cpf, data_nascimento)
    VALUES (p_nome_completo, p_email, p_senha, p_cpf, p_data_nascimento);
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN p_nome_completo VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_senha VARCHAR(100),
    IN p_cpf VARCHAR(14),
    IN p_data_nascimento DATE
)
BEGIN
    INSERT INTO tutor (nome_tutor, email, senha_tutor, cpf, data_nascimento)
    VALUES (p_nome_completo, p_email, p_senha, p_cpf, p_data_nascimento);
END $$

DELIMITER ;
DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN p_nome_completo VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_senha VARCHAR(100),
    IN p_cpf VARCHAR(14),
    IN p_data_nascimento DATE
)
BEGIN
    INSERT INTO tutor (nome_tutor, email, senha_tutor, cpf, data_nascimento)
    VALUES (p_nome_completo, p_email, p_senha, p_cpf, p_data_nascimento);
END $$

DELIMITER ;

DROP PROCEDURE IF EXISTS insert_tutor;

DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN p_nome_completo VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_senha VARCHAR(100),
    IN p_cpf VARCHAR(14),
    IN p_data_nascimento DATE
)
BEGIN
    INSERT INTO tutor (nome_tutor, email, senha_tutor, cpf, data_nascimento)
    VALUES (p_nome_completo, p_email, p_senha, p_cpf, p_data_nascimento);
END $$

DELIMITER ;

CALL insert_tutor('João Silva', 'joao@email.com', 'senha123', '123.456.789-00', '1985-01-01');


-- Garantir que a antiga seja removida
DROP PROCEDURE IF EXISTS insert_tutor;

DELIMITER $$

CREATE PROCEDURE insert_tutor(
    IN p_nome_completo VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_senha VARCHAR(100),
    IN p_cpf VARCHAR(14),
    IN p_data_nascimento DATE
)
BEGIN
    INSERT INTO tutor (
        nome_tutor, 
        email, 
        senha_tutor, 
        cpf, 
        data_nascimento
    )
    VALUES (
        p_nome_completo, 
        p_email, 
        p_senha, 
        p_cpf, 
        p_data_nascimento
    );
END $$

DELIMITER ;

CALL insert_tutor(
    'João Silva',
    'joao@email.com',
    'senha123',
    '123.456.790-00',
    '1985-01-01'
);

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
    ID_CONSULTA INT,
    FOREIGN KEY (ID_TUTOR) REFERENCES tutor(ID),
    FOREIGN KEY (ID_CONSULTA) REFERENCES prontuariopet(ID)
);

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
    ID_CONSULTA INT,
    FOREIGN KEY (ID_TUTOR) REFERENCES tutor(ID),
    FOREIGN KEY (ID_CONSULTA) REFERENCES prontuariopet(ID)
);
USE pet_patrick_db;

CREATE TABLE prontuariopet (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    historico_veterinario VARCHAR(150) NOT NULL,
    motivo_consulta TEXT NOT NULL,
    avaliacao_geral TEXT,
    procedimentos TEXT,
    diagnostico_conslusivo TEXT,
    observacao TEXT
);

SELECT email, COUNT(*)
FROM tutor
GROUP BY email
HAVING COUNT(*) > 1;
SELECT * FROM tutor WHERE email IN ('rayan@gmail.com', 'joao@email.com');

DELETE FROM tutor WHERE email = 'joao@email.com' LIMIT 1;


-- Veterinário
CREATE TABLE `veterinario` (
    `ID` INT AUTO_INCREMENT PRIMARY KEY,
    `NOME` VARCHAR(45) NOT NULL,
    `EMAIL` VARCHAR(45) NOT NULL UNIQUE,
    `CRMV` INT NOT NULL UNIQUE,
    `UF_CRMV` VARCHAR(5) NOT NULL,
    `TELEFONE` BIGINT NOT NULL,
    `PESSOA_JURIDICA_idPESSOA_JURIDICA` INT NOT NULL,
    `PESSOA_FISICA_idPESSOA_FISICA` INT NOT NULL,
    `SENHA_VETERINARIO` VARCHAR(150) NOT NULL,
    FOREIGN KEY (`PESSOA_JURIDICA_idPESSOA_JURIDICA`) REFERENCES `pessoa_juridica`(`ID`),
    FOREIGN KEY (`PESSOA_FISICA_idPESSOA_FISICA`) REFERENCES `pessoa_fisica`(`ID`)
);


CREATE TABLE IF NOT EXISTS pessoa_fisica (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    CPF BIGINT UNIQUE,
    DATA_NASCIMENTO DATE,
    GENERO VARCHAR(45)
);








-- Veterinario
CREATE TABLE IF NOT EXISTS veterinario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(45) NOT NULL,
    EMAIL VARCHAR(45) NOT NULL UNIQUE,
    CRMV INT NOT NULL UNIQUE,
    UF_CRMV VARCHAR(5) NOT NULL,
    TELEFONE BIGINT NOT NULL,
    PESSOA_JURIDICA_idPESSOA_JURIDICA INT NOT NULL,
    PESSOA_FISICA_idPESSOA_FISICA INT NOT NULL,
    SENHA_VETERINARIO VARCHAR(150) NOT NULL,
    FOREIGN KEY (PESSOA_JURIDICA_idPESSOA_JURIDICA) REFERENCES pessoa_juridica(ID),
    FOREIGN KEY (PESSOA_FISICA_idPESSOA_FISICA) REFERENCES pessoa_fisica(ID)
);

SHOW TABLES;

USE pet_patrick_db;

CREATE TABLE IF NOT EXISTS veterinario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(45) NOT NULL,
    EMAIL VARCHAR(45) NOT NULL UNIQUE,
    CRMV INT NOT NULL UNIQUE,
    UF_CRMV VARCHAR(5) NOT NULL,
    TELEFONE BIGINT NOT NULL,
    PESSOA_JURIDICA_idPESSOA_JURIDICA INT NOT NULL,
    PESSOA_FISICA_idPESSOA_FISICA INT NOT NULL,
    SENHA_VETERINARIO VARCHAR(150) NOT NULL,
    FOREIGN KEY (PESSOA_JURIDICA_idPESSOA_JURIDICA) REFERENCES pessoa_juridica(ID),
    FOREIGN KEY (PESSOA_FISICA_idPESSOA_FISICA) REFERENCES pessoa_fisica(ID)
);

DESCRIBE veterinario;
ALTER TABLE veterinario 
CHANGE COLUMN PESSOA_FISICA_idPESSOA_FISICA pessoa_fisica_id INT NOT NULL;

ALTER TABLE veterinario 
CHANGE COLUMN PESSOA_JURIDICA_idPESSOA_JURIDICA pessoa_juridica_id INT NOT NULL;
ALTER TABLE veterinario DROP FOREIGN KEY veterinario_ibfk_1;
ALTER TABLE veterinario ADD CONSTRAINT fk_vet_pf FOREIGN KEY (pessoa_fisica_id) REFERENCES pessoa_fisica(ID);

ALTER TABLE veterinario DROP FOREIGN KEY veterinario_ibfk_2;
ALTER TABLE veterinario ADD CONSTRAINT fk_vet_pj FOREIGN KEY (pessoa_juridica_id) REFERENCES pessoa_juridica(ID);





SHOW CREATE TABLE veterinario;

-- Renomeia coluna PESSOA_FISICA
ALTER TABLE veterinario 
CHANGE COLUMN PESSOA_FISICA_idPESSOA_FISICA pessoa_fisica_id INT NOT NULL;

-- Remove foreign keys antigas duplicadas
ALTER TABLE veterinario DROP FOREIGN KEY veterinario_ibfk_1;
ALTER TABLE veterinario DROP FOREIGN KEY veterinario_ibfk_2;

-- Remove a foreign key antiga fk_vet_pj duplicada, se existir
ALTER TABLE veterinario DROP FOREIGN KEY fk_vet_pj;

-- Adiciona as foreign keys novas corretas
ALTER TABLE veterinario 
ADD CONSTRAINT fk_vet_pf FOREIGN KEY (pessoa_fisica_id) REFERENCES pessoa_fisica(ID);

ALTER TABLE veterinario 
ADD CONSTRAINT fk_vet_pj FOREIGN KEY (pessoa_juridica_id) REFERENCES pessoa_juridica(ID);
-- Mostra as foreign keys da tabela veterinario
SHOW CREATE TABLE veterinario;

DROP TABLE IF EXISTS veterinario;

CREATE TABLE IF NOT EXISTS veterinario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(45) NOT NULL,
    EMAIL VARCHAR(45) NOT NULL UNIQUE,
    CRMV INT NOT NULL UNIQUE,
    UF_CRMV VARCHAR(5) NOT NULL,
    TELEFONE VARCHAR(15) NOT NULL,
    pessoa_juridica_id INT NOT NULL,
    pessoa_fisica_id INT NOT NULL,
    senha_veterinario VARCHAR(150) NOT NULL,
    FOREIGN KEY (pessoa_juridica_id) REFERENCES pessoa_juridica(ID),
    FOREIGN KEY (pessoa_fisica_id) REFERENCES pessoa_fisica(ID)
);

CREATE TABLE IF NOT EXISTS veterinario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NOME VARCHAR(45) NOT NULL,
    EMAIL VARCHAR(45) NOT NULL UNIQUE,
    CRMV INT NOT NULL UNIQUE,
    UF_CRMV VARCHAR(5) NOT NULL,
    TELEFONE VARCHAR(15) NOT NULL,
    pessoa_fisica_id INT NULL,
    pessoa_juridica_id INT NULL,
    senha_veterinario VARCHAR(150) NOT NULL,
    FOREIGN KEY (pessoa_fisica_id) REFERENCES pessoa_fisica(ID),
    FOREIGN KEY (pessoa_juridica_id) REFERENCES pessoa_juridica(ID)
);
ALTER TABLE veterinario 
    MODIFY pessoa_fisica_id INT NULL,
    MODIFY pessoa_juridica_id INT NULL;

SHOW CREATE TABLE pessoa_fisica;
SHOW CREATE TABLE pessoa_juridica;

ALTER TABLE pessoa_fisica MODIFY ID INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE pessoa_juridica MODIFY ID INT AUTO_INCREMENT PRIMARY KEY;

SHOW TABLES;
DESCRIBE veterinario;

