-- Tabela de Processos Seletivos (Associações de Candidatos a Vagas) no Sistema KAN
CREATE TABLE IF NOT EXISTS processos_seletivos (
    id BIGSERIAL PRIMARY KEY,
    vaga_id BIGINT NOT NULL REFERENCES vagas(id) ON DELETE CASCADE UNIQUE,
    empresa TEXT NOT NULL,
    candidatos JSONB DEFAULT '[]'::jsonb NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar Row Level Security (RLS) e permissões de acesso
ALTER TABLE processos_seletivos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso total a processos_seletivos" ON processos_seletivos;
CREATE POLICY "Permitir acesso total a processos_seletivos" ON processos_seletivos FOR ALL USING (true) WITH CHECK (true);

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';
