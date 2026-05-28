-- Script para adicionar a coluna foto_base64 na tabela de equipes
ALTER TABLE equipes ADD COLUMN IF NOT EXISTS foto_base64 TEXT;

-- Notifica PostgREST para recarregar o schema
NOTIFY pgrst, 'reload schema';
