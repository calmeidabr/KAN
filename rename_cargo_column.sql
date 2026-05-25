-- Migration to rename cargo to profissao and add a new cargo column
ALTER TABLE mapas_salvos RENAME COLUMN cargo TO profissao;
ALTER TABLE mapas_salvos ADD COLUMN IF NOT EXISTS cargo TEXT DEFAULT NULL;
NOTIFY pgrst, 'reload schema';
