CREATE TABLE IF NOT EXISTS `db_pet`.`TUTOR` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `NOME_TUTOR` VARCHAR(45) NOT NULL,
  `CPF` INT(11) NOT NULL,
  `EMAIL` VARCHAR(45) NOT NULL,
  `ENDEREÇO` VARCHAR(100) NOT NULL,
  `DATA_NASCIMENTO` DATE NULL,
  `ID_FEEDBACK_SISTEMA` INT NULL,
  `ID_FEEDBACK_PET` INT NULL,
  PRIMARY KEY (`ID`),
  INDEX `fk_TUTOR_FEEDBACK1_idx` (`ID_FEEDBACK_SISTEMA` ASC) VISIBLE,
  INDEX `fk_TUTOR_FEEDBACK_PET1_idx` (`ID_FEEDBACK_PET` ASC) VISIBLE,
  UNIQUE INDEX `CPF_UNIQUE` (`CPF` ASC) VISIBLE,
  CONSTRAINT `fk_TUTOR_FEEDBACK1`
    FOREIGN KEY (`ID_FEEDBACK_SISTEMA`)
    REFERENCES `db_pet`.`FEEDBACK` (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_TUTOR_FEEDBACK_PET1`
    FOREIGN KEY (`ID_FEEDBACK_PET`)
    REFERENCES `db_pet`.`FEEDBACK_PET` (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `db_pet`.`CONTATO_TUTOR` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `ID_TUTOR` INT NOT NULL,
  `TIPO_CONTATO` ENUM('CELULAR', 'FIXO', 'WHATSAPP', 'TELEGRAM', 'EMAIL_SECUNDARIO') NOT NULL DEFAULT 'CELULAR',
  `DDD` CHAR(2) NOT NULL,           -- 11, 21, 31 etc.
  `NUMERO` VARCHAR(9) NOT NULL,     -- 9xxxx-xxxx ou 3xxx-xxxx
  `DATA_CADASTRO` DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`ID`),
  
  -- Chave composta para garantir que o mesmo tutor não cadastre o mesmo número duas vezes
  UNIQUE INDEX `UK_TUTOR_NUMERO` (`ID_TUTOR`, `DDD`, `NUMERO`),
  
  -- Relacionamento com a tabela TUTOR
  CONSTRAINT `FK_CONTATO_TUTOR_TUTOR` 
    FOREIGN KEY (`ID_TUTOR`) 
    REFERENCES `db_pet`.`TUTOR` (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE

);

SELECT * FROM CONTATO_TUTOR;

DELIMITER $$

CREATE PROCEDURE insert_tutor (
    p_nome_tutor VARCHAR(80),
    p_cpf_tutor CHAR(14),       
    p_email_tutor VARCHAR(80),
    p_endereco VARCHAR(100),
    p_data_nascimento DATE,
    p_senha_tutor VARCHAR(150)
)
BEGIN
    -- Validação de campos obrigatórios e não vazios
    IF p_nome_tutor IS NULL OR TRIM(p_nome_tutor) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O nome do tutor é obrigatório';
    END IF;

    IF p_cpf_tutor IS NULL OR p_cpf_tutor NOT REGEXP '^[0-9]{11}$' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O CPF deve conter exatamente 11 dígitos numéricos';
    END IF;

    IF p_email_tutor IS NULL OR TRIM(p_email_tutor) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O email do tutor é obrigatório';
    END IF;

    IF p_endereco IS NULL OR TRIM(p_endereco) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'O endereço do tutor é obrigatório';
    END IF;

    IF p_data_nascimento IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A data de nascimento do tutor é obrigatória';
    END IF;
    
    IF p_senha_tutor IS NULL OR TRIM(p_nome_tutor) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A senha do tutor é obrigatório';
    END IF;

    -- Verifica se já existe email ou CPF cadastrado
    IF EXISTS (SELECT 1 FROM tutor WHERE email = p_email_tutor) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Email já cadastrado no sistema';
    END IF;

    IF EXISTS (SELECT 1 FROM tutor WHERE CPF = p_cpf_tutor) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CPF já cadastrado no sistema';
    END IF;

    -- Inserção
    INSERT INTO tutor (nome_tutor, CPF, email, endereco, data_nascimento, senha_tutor)
    VALUES (p_nome_tutor, p_cpf_tutor, p_email_tutor, p_endereco, p_data_nascimento, p_senha_tutor);

END$$

DELIMITER ;

CALL insert_tutor('Patrick Nascimento', '00055879814', 'patrick54682366@edu.pa.senac.br', 'Icoaraci', '2004-03-16');

SELECT * FROM tutor;


ALTER TABLE tutor
ADD imagem_perfil_tutor VARCHAR(80);

ALTER TABLE pet
RENAME COLUMN RAÇA TO raca;