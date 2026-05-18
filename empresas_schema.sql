-- Tabela de Empresas do Sistema KAN
CREATE TABLE IF NOT EXISTS empresas (
    id BIGSERIAL PRIMARY KEY,
    nome_empresa TEXT NOT NULL,
    razao_social TEXT,
    cnpj TEXT UNIQUE,
    segmento TEXT,
    num_colaboradores TEXT,
    site TEXT,
    telefone TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inserção de Registros Iniciais de Exemplo caso a tabela esteja vazia
INSERT INTO empresas (nome_empresa, razao_social, cnpj, segmento, num_colaboradores, site, telefone, email)
VALUES 
('Mundo KAN', 'Mundo KAN Tecnologia Ltda', '00.000.000/0001-00', 'Tecnologia', '50', 'https://mundokan.com.br', '(11) 99999-9999', 'contato@mundokan.com.br'),
('Empresa Cliente A', 'Cliente A Varejo S/A', '11.111.111/0001-11', 'Varejo', '500', 'https://clientea.com', '(11) 88888-8888', 'rh@clientea.com')
ON CONFLICT (cnpj) DO NOTHING;
