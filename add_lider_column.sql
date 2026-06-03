-- Adiciona a coluna 'lider' na tabela mapas_salvos para controle de liderança nos departamentos
ALTER TABLE mapas_salvos ADD COLUMN IF NOT EXISTS lider BOOLEAN DEFAULT FALSE;

-- Atualiza o cache do PostgREST (Supabase) para que a nova coluna fique visível imediatamente
NOTIFY pgrst, 'reload schema';
