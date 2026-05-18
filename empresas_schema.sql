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
    responsavel_nome TEXT,
    responsavel_celular TEXT,
    responsavel_email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Adiciona colunas caso a tabela já exista em produção
ALTER TABLE empresas ADD COLUMN IF NOT EXISTS responsavel_nome TEXT;
ALTER TABLE empresas ADD COLUMN IF NOT EXISTS responsavel_celular TEXT;
ALTER TABLE empresas ADD COLUMN IF NOT EXISTS responsavel_email TEXT;

-- Atualiza o cache de schema do PostgREST (Supabase API) instantaneamente
NOTIFY pgrst, 'reload schema';

-- Inserção de Registros Iniciais de Exemplo caso a tabela esteja vazia
INSERT INTO empresas (nome_empresa, razao_social, cnpj, segmento, num_colaboradores, site, telefone, email, responsavel_nome, responsavel_celular, responsavel_email)
VALUES 
('Mundo KAN', 'Mundo KAN Tecnologia Ltda', '00.000.000/0001-00', 'Tecnologia', '50', 'https://mundokan.com.br', '(11) 99999-9999', 'contato@mundokan.com.br', 'Administrador KAN', '(11) 99999-9999', 'adminkan@mundokan.com.br'),
('Empresa Cliente A', 'Cliente A Varejo S/A', '11.111.111/0001-11', 'Varejo', '500', 'https://clientea.com', '(11) 88888-8888', 'rh@clientea.com', 'Maria da Silva', '(11) 97777-7777', 'maria@clientea.com')
ON CONFLICT (cnpj) DO NOTHING;
