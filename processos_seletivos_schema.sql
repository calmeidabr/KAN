-- Tabela de Processos Seletivos (Associações de Candidatos a Vagas) no Sistema KAN
CREATE TABLE IF NOT EXISTS processos_seletivos (
    id BIGSERIAL PRIMARY KEY,
    vaga_id BIGINT NOT NULL REFERENCES vagas(id) ON DELETE CASCADE UNIQUE,
    empresa TEXT NOT NULL,
    candidatos JSONB DEFAULT '[]'::jsonb NOT NULL,
    perfis_ideais JSONB DEFAULT NULL,
    categorias_ideais JSONB DEFAULT NULL,
    qualidades_ideais JSONB DEFAULT NULL,
    kan_ideal JSONB DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Adicionar colunas caso a tabela já exista na base de dados do usuário
ALTER TABLE processos_seletivos ADD COLUMN IF NOT EXISTS perfis_ideais JSONB DEFAULT NULL;
ALTER TABLE processos_seletivos ADD COLUMN IF NOT EXISTS categorias_ideais JSONB DEFAULT NULL;
ALTER TABLE processos_seletivos ADD COLUMN IF NOT EXISTS qualidades_ideais JSONB DEFAULT NULL;
ALTER TABLE processos_seletivos ADD COLUMN IF NOT EXISTS kan_ideal JSONB DEFAULT NULL;

-- Converte a coluna kan_ideal para JSONB se ela for do tipo TEXT para suportar múltiplos KANs
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'processos_seletivos' 
          AND column_name = 'kan_ideal' 
          AND data_type = 'text'
    ) THEN
        ALTER TABLE processos_seletivos 
        ALTER COLUMN kan_ideal TYPE JSONB 
        USING CASE 
            WHEN kan_ideal IS NULL OR kan_ideal = 'Nenhum' THEN NULL
            WHEN kan_ideal LIKE '[%' THEN kan_ideal::jsonb
            ELSE jsonb_build_array(kan_ideal)
        END;
    END IF;
END $$;

-- Habilitar Row Level Security (RLS) e permissões de acesso
ALTER TABLE processos_seletivos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso total a processos_seletivos" ON processos_seletivos;
CREATE POLICY "Permitir acesso total a processos_seletivos" ON processos_seletivos FOR ALL USING (true) WITH CHECK (true);

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';
