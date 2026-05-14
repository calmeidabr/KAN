-- Criação das tabelas para gestão de banners e assets

CREATE TABLE IF NOT EXISTS kan_assets (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE,
    data_base64 TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kan_banners (
    id INTEGER PRIMARY KEY, -- 1, 2, 3
    title TEXT,
    subtitle TEXT,
    cta_text TEXT,
    cta_link TEXT,
    accent_color TEXT,
    asset_id INTEGER REFERENCES kan_assets(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inserção inicial de banners se não existirem
INSERT INTO kan_banners (id, title, subtitle, cta_text, cta_link, accent_color)
VALUES 
(1, 'Diagnóstico Inteligente', 'Análise comportamental profunda e instantânea.', 'Explorar Diagnósticos', '#', '#F18617'),
(2, 'Gestão de Talentos', 'Dados precisos para equipes de alta performance.', 'Ver Equipes', '#', '#00d2ff'),
(3, 'Inovação Humana', 'A inteligência por trás do comportamento.', 'Saiba Mais', '#', '#39ff14')
ON CONFLICT (id) DO NOTHING;
