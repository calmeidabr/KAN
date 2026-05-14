-- ========================================================
-- SCHEMA PARA SISTEMA KAN SAAS (MULTI-TENANT)
-- ========================================================

-- 1. Tabela de Entidades (Empresas/Tenants)
CREATE TABLE IF NOT EXISTS kan_entidades (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    documento TEXT, -- CNPJ/CPF
    status TEXT DEFAULT 'Ativo', -- Ativo, Suspenso, Desativado
    plano TEXT DEFAULT 'Standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Usuários do Sistema
CREATE TABLE IF NOT EXISTS kan_usuarios (
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL, -- Administrador Master, Administrador Empresa, Usuário
    status TEXT DEFAULT 'Ativo',
    entidade_id INTEGER REFERENCES kan_entidades(id),
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Biblioteca de Imagens (Assets)
CREATE TABLE IF NOT EXISTS kan_assets (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE,
    data_base64 TEXT, -- Armazena a imagem em base64 para carregamento rápido
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Configuração de Banners da Home
CREATE TABLE IF NOT EXISTS kan_banners (
    id INTEGER PRIMARY KEY, -- 1, 2, 3...
    title TEXT,
    subtitle TEXT,
    cta_text TEXT,
    cta_link TEXT DEFAULT '#',
    accent_color TEXT DEFAULT '#F18617',
    asset_id INTEGER REFERENCES kan_assets(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================
-- INSERÇÕES INICIAIS (DADOS DE EXEMPLO E ADMIN)
-- ========================================================

-- Inserir Entidade Master
INSERT INTO kan_entidades (nome, status, plano) 
VALUES ('KAN Master', 'Ativo', 'Enterprise')
ON CONFLICT (nome) DO NOTHING;

-- Inserir Usuários Iniciais (Senhas originais mantidas)
INSERT INTO kan_usuarios (usuario, senha, tipo, entidade_id)
VALUES 
('adminkan', 'K@nAdmin#2026*', 'Administrador Master', (SELECT id FROM kan_entidades WHERE nome = 'KAN Master')),
('cristiano', 'kan2026', 'Administrador Empresa', (SELECT id FROM kan_entidades WHERE nome = 'KAN Master')),
('maria', 'maria2026', 'Usuário', (SELECT id FROM kan_entidades WHERE nome = 'KAN Master'))
ON CONFLICT (usuario) DO NOTHING;

-- Inserir Banners Iniciais
INSERT INTO kan_banners (id, title, subtitle, cta_text, cta_link, accent_color)
VALUES 
(1, 'Diagnóstico Inteligente', 'Análise comportamental profunda e instantânea.', 'Explorar Diagnósticos', '#', '#F18617'),
(2, 'Gestão de Talentos', 'Dados precisos para equipes de alta performance.', 'Ver Equipes', '#', '#00d2ff'),
(3, 'Inovação Humana', 'A inteligência por trás do comportamento.', 'Saiba Mais', '#', '#39ff14')
ON CONFLICT (id) DO NOTHING;
