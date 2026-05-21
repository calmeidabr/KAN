-- Tabela de Vagas para as Empresas no Sistema KAN
CREATE TABLE IF NOT EXISTS vagas (
    id BIGSERIAL PRIMARY KEY,
    nome_vaga TEXT NOT NULL,
    senioridade TEXT NOT NULL,
    link_vaga TEXT,
    empresa TEXT NOT NULL,
    departamento TEXT,
    kan_ideal TEXT,
    perfis_ideais JSONB DEFAULT '[]'::jsonb,
    categorias_ideais JSONB DEFAULT '[]'::jsonb,
    qualidades_ideais JSONB DEFAULT '[]'::jsonb,
    descricao_vaga TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permissões padrão
ALTER TABLE vagas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso total a vagas" ON vagas;
CREATE POLICY "Permitir acesso total a vagas" ON vagas FOR ALL USING (true) WITH CHECK (true);

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';
