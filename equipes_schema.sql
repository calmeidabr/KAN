-- =============================================================
-- Tabela de Equipes no Sistema KAN
-- Execute este script no SQL Editor do Supabase
-- =============================================================

CREATE TABLE IF NOT EXISTS equipes (
    id          BIGSERIAL PRIMARY KEY,
    nome        TEXT UNIQUE NOT NULL,
    empresa     TEXT DEFAULT NULL,
    departamento TEXT DEFAULT NULL,
    membros     JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices úteis
CREATE INDEX IF NOT EXISTS idx_equipes_empresa ON equipes (empresa);
CREATE INDEX IF NOT EXISTS idx_equipes_nome ON equipes (nome);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_equipes_updated_at ON equipes;
CREATE TRIGGER trg_equipes_updated_at
    BEFORE UPDATE ON equipes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Segurança RLS: acesso total para usuários autenticados
ALTER TABLE equipes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Acesso total equipes" ON equipes;
CREATE POLICY "Acesso total equipes"
    ON equipes FOR ALL
    USING (true)
    WITH CHECK (true);

-- Notifica PostgREST para recarregar o schema
NOTIFY pgrst, 'reload schema';
