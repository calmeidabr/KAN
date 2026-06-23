-- =========================================================================
-- SCRIPT DE MIGRAÇÃO: CRIAÇÃO DE TABELA DE PLANOS E LIMITE DINDÂMICO
-- Execute este script no SQL Editor do seu painel do Supabase.
-- =========================================================================

-- 1. Criar a tabela de planos
CREATE TABLE IF NOT EXISTS public.planos (
    id                 TEXT PRIMARY KEY,
    nome               TEXT NOT NULL,
    max_usuarios       INT NOT NULL,
    max_talentos       INT NOT NULL,
    max_processos_ano  INT NOT NULL,
    max_equipes        INT NOT NULL,
    custo_mensal       NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Inserir dados iniciais dos planos
INSERT INTO public.planos (id, nome, max_usuarios, max_talentos, max_processos_ano, max_equipes, custo_mensal) VALUES
('free', 'Free', 1, 5, 1, 0, 0.00),
('start', 'Start', 1, 10, 3, 3, 179.00),
('intermediario', 'Intermediário', 3, 50, 10, 10, 359.00),
('business', 'Business', 10, 100, 30, 30, 719.00),
('pro', 'Pro', 15, 300, 50, 70, 1979.00),
('alta_performance', 'Alta Performance', 15, 700, 75, 100, 2429.00)
ON CONFLICT (id) DO UPDATE SET 
    nome = EXCLUDED.nome,
    max_usuarios = EXCLUDED.max_usuarios,
    max_talentos = EXCLUDED.max_talentos,
    max_processos_ano = EXCLUDED.max_processos_ano,
    max_equipes = EXCLUDED.max_equipes,
    custo_mensal = EXCLUDED.custo_mensal;

-- 3. Habilitar RLS na tabela planos (Leitura livre para usuários autenticados, Escrita restrita)
ALTER TABLE public.planos ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Leitura livre de planos" ON public.planos;
CREATE POLICY "Leitura livre de planos" ON public.planos
    FOR SELECT TO authenticated USING (true);

-- 4. Ajustar restrição de planos na tabela tenants
ALTER TABLE public.tenants DROP CONSTRAINT IF EXISTS tenants_tier_check;

-- Garantir que todos estejam em 'free' ou 'alta_performance' antes da chave estrangeira
UPDATE public.tenants SET tier = 'free' WHERE tier = 'basic';
UPDATE public.tenants SET tier = 'alta_performance' WHERE tier = 'premium';

-- Configurar padrão da coluna tier para 'free'
ALTER TABLE public.tenants ALTER COLUMN tier SET DEFAULT 'free';

-- Criar chave estrangeira ligando a tabela tenants à tabela planos
ALTER TABLE public.tenants DROP CONSTRAINT IF EXISTS fk_tenants_plan;
ALTER TABLE public.tenants ADD CONSTRAINT fk_tenants_plan 
FOREIGN KEY (tier) REFERENCES public.planos(id) ON UPDATE CASCADE;

-- 5. Atualizar a função handle_new_user() para cadastrar novos tenants no plano 'free'
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER 
SECURITY DEFINER
AS $$
DECLARE
    new_tenant_id UUID;
    slug_val TEXT;
    full_name_val TEXT;
    username_val TEXT;
    direitos_val TEXT := 'Comum';
BEGIN
    full_name_val := coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1));
    username_val := split_part(new.email, '@', 1);

    -- Se o e-mail for do domínio @mundokan.com.br, associa ao tenant padrão Mundo KAN Workspace
    IF new.email LIKE '%@mundokan.com.br' THEN
        IF username_val = 'adminkan' THEN
            direitos_val := 'admin master';
        ELSIF username_val IN ('admin', 'cristiano') THEN
            direitos_val := 'Editor';
        ELSIF username_val = 'maria' THEN
            direitos_val := 'Analista';
        END IF;

        INSERT INTO public.usuarios (id, usuario, nome_completo, email, tenant_id, is_main_user, direitos, status)
        VALUES (
            new.id, 
            username_val, 
            full_name_val, 
            new.email, 
            '00000000-0000-0000-0000-000000000000', 
            TRUE, 
            direitos_val, 
            'Ativo'
        )
        ON CONFLICT (id) DO NOTHING;
        RETURN NEW;
    END IF;

    -- Para outros clientes, cria um novo Tenant no plano 'free'
    slug_val := username_val || '-' || floor(random() * 10000)::text;

    -- 1. Insere o Workspace padrão para o novo cliente (Tier free por padrão)
    INSERT INTO public.tenants (name, slug, tier)
    VALUES (full_name_val || ' Workspace', slug_val, 'free')
    RETURNING id INTO new_tenant_id;

    -- 2. Insere o perfil na tabela public.usuarios
    INSERT INTO public.usuarios (id, usuario, nome_completo, email, tenant_id, is_main_user, direitos, status)
    VALUES (new.id, username_val, full_name_val, new.email, new_tenant_id, TRUE, 'Comum', 'Ativo')
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. Recarregar o schema do PostgREST
NOTIFY pgrst, 'reload schema';
