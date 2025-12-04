DELIMITER $$

CREATE PROCEDURE insert_tutor (
    p_nome_tutor VARCHAR(80),
    p_cpf_tutor CHAR(11),       
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