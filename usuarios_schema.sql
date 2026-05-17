-- Tabela de Usuários do Sistema KAN
CREATE TABLE IF NOT EXISTS usuarios (
    id BIGSERIAL PRIMARY KEY,
    usuario TEXT UNIQUE NOT NULL,
    nome_completo TEXT,
    data_nascimento TEXT,
    empresa TEXT,
    cargo TEXT,
    departamento TEXT,
    direitos TEXT DEFAULT 'Comum', -- Editor / Analista / Comum / admin master
    status TEXT DEFAULT 'Ativo', -- Ativo / Inativo
    foto TEXT DEFAULT '👤', -- Base64 ou Emoji/Placeholder
    grupo TEXT DEFAULT 'Geral', -- Geral / Empresas
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inserção de Registros Iniciais de Exemplo caso a tabela esteja vazia
INSERT INTO usuarios (usuario, nome_completo, data_nascimento, empresa, cargo, departamento, direitos, status, foto, grupo)
VALUES 
('adminkan', 'Administrador Master KAN', '01/01/1980', 'Mundo KAN', 'CEO / Master Admin', 'Diretoria', 'admin master', 'Ativo', '👑', 'Geral'),
('cristiano', 'Cristiano Almeida', '15/05/1985', 'Mundo KAN', 'Gestor de Sistemas', 'Tecnologia', 'Editor', 'Ativo', '👤', 'Geral'),
('maria', 'Maria da Silva', '20/08/1990', 'Empresa Cliente A', 'Analista de RH', 'Recursos Humanos', 'Analista', 'Ativo', '👤', 'Geral'),
('empresa_demo', 'Tech Corp Brasil Ltda', '10/10/2000', 'Tech Corp', 'Conta Empresarial', 'Operações', 'Comum', 'Ativo', '🏢', 'Empresas')
ON CONFLICT (usuario) DO NOTHING;
