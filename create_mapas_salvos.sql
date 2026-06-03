-- Tabela de Talentos (mapas_salvos) do Sistema KAN
CREATE TABLE IF NOT EXISTS mapas_salvos (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    data_nascimento TEXT,
    cargo TEXT,
    grupo TEXT,
    empresa TEXT DEFAULT NULL,
    departamento TEXT DEFAULT NULL,
    linkedin_url TEXT,
    experiencias TEXT,
    foto_base64 TEXT,
    ai_diagnosis TEXT,
    perfil_json TEXT,
    usuario TEXT,
    lider BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Habilita RLS por padrão para proteger os dados (Apenas service_role terá acesso se nenhuma política pública for definida)
ALTER TABLE mapas_salvos ENABLE ROW LEVEL SECURITY;

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';
