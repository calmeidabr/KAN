-- Tabela de Equipes no Sistema KAN
CREATE TABLE IF NOT EXISTS equipes (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    empresa TEXT DEFAULT NULL,
    departamento TEXT DEFAULT NULL,
    membros JSONB DEFAULT '[]'::jsonb, -- Armazena a lista de nomes dos talentos vinculados à equipe
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permissões padrão e segurança RLS
ALTER TABLE equipes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso total a equipes" ON equipes;
CREATE POLICY "Permitir acesso total a equipes" ON equipes FOR ALL USING (true) WITH CHECK (true);

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';
