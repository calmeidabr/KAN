-- Tabela de Usuários do Sistema KAN
CREATE TABLE IF NOT EXISTS usuarios (
    id BIGSERIAL PRIMARY KEY,
    usuario TEXT UNIQUE NOT NULL,
    nome_completo TEXT,
    email TEXT,
    celular TEXT,
    data_nascimento TEXT,
    empresa TEXT,
    cargo TEXT,
    departamento TEXT,
    direitos TEXT DEFAULT 'Comum', -- Editor / Analista / Comum / admin master
    status TEXT DEFAULT 'Ativo', -- Ativo / Inativo
    foto TEXT DEFAULT '☖', -- Base64 ou Emoji/Placeholder
    grupo TEXT DEFAULT 'Geral', -- Geral / Empresas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Adiciona colunas caso a tabela já tenha sido criada anteriormente em produção
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email TEXT;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS celular TEXT;

-- Atualiza o cache de schema do PostgREST (Supabase API) instantaneamente
NOTIFY pgrst, 'reload schema';

-- Inserção de Registros Iniciais de Exemplo caso a tabela esteja vazia
INSERT INTO usuarios (usuario, nome_completo, email, celular, data_nascimento, empresa, cargo, departamento, direitos, status, foto, grupo)
VALUES 
('adminkan', 'Administrador Master KAN', 'adminkan@mundokan.com.br', '(11) 99999-9999', '01/01/1980', 'Mundo KAN', 'CEO / Master Admin', 'Diretoria', 'admin master', 'Ativo', '☖', 'Geral'),
('cristiano', 'Cristiano Almeida', 'cristiano@mundokan.com.br', '(11) 98888-8888', '15/05/1985', 'Mundo KAN', 'Gestor de Sistemas', 'Tecnologia', 'Editor', 'Ativo', '☖', 'Geral'),
('maria', 'Maria da Silva', 'maria@mundokan.com.br', '(11) 97777-7777', '20/08/1990', 'Empresa Cliente A', 'Analista de RH', 'Recursos Humanos', 'Analista', 'Ativo', '☖', 'Geral'),
('empresa_demo', 'Tech Corp Brasil Ltda', 'contato@techcorp.com', '(11) 96666-6666', '10/10/2000', 'Tech Corp', 'Conta Empresarial', 'Operações', 'Comum', 'Ativo', '⛶', 'Empresas')
ON CONFLICT (usuario) DO NOTHING;
