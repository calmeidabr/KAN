-- =============================================================
-- Script de Migração: Adiciona suporte a Harmonia de Equipes no Processo Seletivo
-- Execute este script no SQL Editor do Supabase para atualizar a tabela
-- =============================================================

-- Adiciona a coluna equipe (armazena o nome da equipe associada)
ALTER TABLE processos_seletivos ADD COLUMN IF NOT EXISTS equipe TEXT DEFAULT NULL;

-- Adiciona a coluna historico_harmonia (armazena lista de analises e observacoes em JSONB)
ALTER TABLE processos_seletivos ADD COLUMN IF NOT EXISTS historico_harmonia JSONB DEFAULT '[]'::jsonb NOT NULL;

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';
