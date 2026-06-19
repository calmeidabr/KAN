-- =========================================================================
-- SCRIPT DE MIGRAÇÃO: SAAS MULTI-TENANT COM ROW LEVEL SECURITY (RLS)
-- Execute este script no SQL Editor do seu painel do Supabase.
-- =========================================================================

-- 1. CRIAR TABELA DE TENANTS (Organizações/Clientes)
CREATE TABLE IF NOT EXISTS public.tenants (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL,
    slug       TEXT UNIQUE NOT NULL,
    tier       TEXT NOT NULL CHECK (tier IN ('basic', 'premium')) DEFAULT 'basic',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. INSERIR TENANT PADRÃO "Mundo KAN Workspace" para os dados legados
INSERT INTO public.tenants (id, name, slug, tier)
VALUES ('00000000-0000-0000-0000-000000000000', 'Mundo KAN Workspace', 'mundo-kan', 'premium')
ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, tier = EXCLUDED.tier;

-- 3. CRIAR/REESTRUTURAR A TABELA DE USUÁRIOS (vinculada ao Supabase Auth)
CREATE TABLE IF NOT EXISTS public.usuarios (
    id             UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    usuario        TEXT UNIQUE NOT NULL,
    nome_completo  TEXT,
    email          TEXT UNIQUE NOT NULL,
    celular        TEXT,
    data_nascimento TEXT,
    empresa        TEXT,
    cargo          TEXT,
    departamento   TEXT,
    direitos       TEXT DEFAULT 'Comum' CHECK (direitos IN ('Comum', 'Editor', 'Analista', 'admin master')),
    status         TEXT DEFAULT 'Ativo' CHECK (status IN ('Ativo', 'Inativo')),
    foto           TEXT DEFAULT '☖',
    grupo          TEXT DEFAULT 'Geral',
    tenant_id      UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    is_main_user   BOOLEAN DEFAULT FALSE,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    updated_at     TIMESTAMPTZ DEFAULT NOW()
);

-- 4. FUNÇÕES AUXILIARES DE RLS (SECURITY DEFINER)
-- Devem ser criadas antes de definir os defaults das tabelas de negócio.
CREATE OR REPLACE FUNCTION public.get_my_tenant_id()
RETURNS UUID 
SECURITY DEFINER
AS $$
BEGIN
    RETURN (SELECT tenant_id FROM public.usuarios WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.is_adminkan()
RETURNS BOOLEAN 
SECURITY DEFINER
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.usuarios 
        WHERE id = auth.uid() AND direitos = 'admin master'
    );
END;
$$ LANGUAGE plpgsql;

-- 5. ADICIONAR COLUNA tenant_id NAS TABELAS DE NEGÓCIO COM VALOR DEFAULT AUTOMÁTICO
-- O valor default public.get_my_tenant_id() garante que novas linhas inseridas pelo
-- Streamlit recebam automaticamente o ID do tenant correto do usuário logado.
ALTER TABLE public.tenants ADD COLUMN IF NOT EXISTS tier TEXT NOT NULL CHECK (tier IN ('basic', 'premium')) DEFAULT 'basic';
ALTER TABLE public.equipes ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE DEFAULT public.get_my_tenant_id();
ALTER TABLE public.vagas ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE DEFAULT public.get_my_tenant_id();
ALTER TABLE public.processos_seletivos ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE DEFAULT public.get_my_tenant_id();
ALTER TABLE public.mapas_salvos ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE DEFAULT public.get_my_tenant_id();
ALTER TABLE public.empresas ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE DEFAULT public.get_my_tenant_id();
ALTER TABLE public.hierarquia_departamentos ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE DEFAULT public.get_my_tenant_id();

-- 6. MIGRAR DADOS LEGADOS EXISTENTES PARA O TENANT PADRÃO
UPDATE public.equipes SET tenant_id = '00000000-0000-0000-0000-000000000000' WHERE tenant_id IS NULL;
UPDATE public.vagas SET tenant_id = '00000000-0000-0000-0000-000000000000' WHERE tenant_id IS NULL;
UPDATE public.processos_seletivos SET tenant_id = '00000000-0000-0000-0000-000000000000' WHERE tenant_id IS NULL;
UPDATE public.mapas_salvos SET tenant_id = '00000000-0000-0000-0000-000000000000' WHERE tenant_id IS NULL;
UPDATE public.empresas SET tenant_id = '00000000-0000-0000-0000-000000000000' WHERE tenant_id IS NULL;
UPDATE public.hierarquia_departamentos SET tenant_id = '00000000-0000-0000-0000-000000000000' WHERE tenant_id IS NULL;

-- 7. TORNAR tenant_id OBRIGATÓRIO (NOT NULL) E DEFINIR DEFAULT APÓS MIGRAÇÃO
ALTER TABLE public.equipes ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE public.vagas ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE public.processos_seletivos ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE public.mapas_salvos ALTER COLUMN tenant_id SET NOT NULL;

-- 8. HABILITAR ROW LEVEL SECURITY (RLS) NAS TABELAS
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.equipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vagas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processos_seletivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mapas_salvos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hierarquia_departamentos ENABLE ROW LEVEL SECURITY;

-- 9. CONFIGURAR AS POLÍTICAS DE RLS

-- Políticas para tenants
DROP POLICY IF EXISTS "Acesso tenants" ON public.tenants;
CREATE POLICY "Acesso tenants" ON public.tenants
    FOR SELECT TO authenticated
    USING (public.is_adminkan() OR id = public.get_my_tenant_id());

-- Políticas para usuários
DROP POLICY IF EXISTS "Leitura de usuários do mesmo tenant" ON public.usuarios;
CREATE POLICY "Leitura de usuários do mesmo tenant" ON public.usuarios
    FOR SELECT TO authenticated
    USING (public.is_adminkan() OR tenant_id = public.get_my_tenant_id());

DROP POLICY IF EXISTS "Modificação de usuários por admin ou main user" ON public.usuarios;
CREATE POLICY "Modificação de usuários por admin ou main user" ON public.usuarios
    FOR ALL TO authenticated
    USING (
        public.is_adminkan() OR 
        (tenant_id = public.get_my_tenant_id() AND EXISTS (
            SELECT 1 FROM public.usuarios 
            WHERE id = auth.uid() AND is_main_user = TRUE
        ))
    );

-- Políticas para dados de negócio (Equipes, Vagas, Processos, Mapas, Empresas, Organograma)
DROP POLICY IF EXISTS "tenant_isolation_equipes" ON public.equipes;
CREATE POLICY "tenant_isolation_equipes" ON public.equipes
    FOR ALL TO authenticated
    USING (public.is_adminkan() OR tenant_id = public.get_my_tenant_id())
    WITH CHECK (public.is_adminkan() OR tenant_id = public.get_my_tenant_id());

DROP POLICY IF EXISTS "tenant_isolation_vagas" ON public.vagas;
CREATE POLICY "tenant_isolation_vagas" ON public.vagas
    FOR ALL TO authenticated
    USING (public.is_adminkan() OR tenant_id = public.get_my_tenant_id())
    WITH CHECK (public.is_adminkan() OR tenant_id = public.get_my_tenant_id());

DROP POLICY IF EXISTS "tenant_isolation_processos" ON public.processos_seletivos;
CREATE POLICY "tenant_isolation_processos" ON public.processos_seletivos
    FOR ALL TO authenticated
    USING (public.is_adminkan() OR tenant_id = public.get_my_tenant_id())
    WITH CHECK (public.is_adminkan() OR tenant_id = public.get_my_tenant_id());

DROP POLICY IF EXISTS "tenant_isolation_mapas" ON public.mapas_salvos;
CREATE POLICY "tenant_isolation_mapas" ON public.mapas_salvos
    FOR ALL TO authenticated
    USING (public.is_adminkan() OR tenant_id = public.get_my_tenant_id())
    WITH CHECK (public.is_adminkan() OR tenant_id = public.get_my_tenant_id());

DROP POLICY IF EXISTS "tenant_isolation_empresas" ON public.empresas;
CREATE POLICY "tenant_isolation_empresas" ON public.empresas
    FOR ALL TO authenticated
    USING (public.is_adminkan() OR tenant_id = public.get_my_tenant_id())
    WITH CHECK (public.is_adminkan() OR tenant_id = public.get_my_tenant_id());

DROP POLICY IF EXISTS "tenant_isolation_hierarquia" ON public.hierarquia_departamentos;
CREATE POLICY "tenant_isolation_hierarquia" ON public.hierarquia_departamentos
    FOR ALL TO authenticated
    USING (public.is_adminkan() OR tenant_id = public.get_my_tenant_id())
    WITH CHECK (public.is_adminkan() OR tenant_id = public.get_my_tenant_id());


-- 10. TRIGGER PARA AUTO-CADASTRO (ONBOARDING VIA SITE)
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

    -- Para outros clientes, cria um novo Tenant básico
    slug_val := username_val || '-' || floor(random() * 10000)::text;

    -- 1. Insere o Workspace padrão para o novo cliente (Tier básico por padrão)
    INSERT INTO public.tenants (name, slug, tier)
    VALUES (full_name_val || ' Workspace', slug_val, 'basic')
    RETURNING id INTO new_tenant_id;

    -- 2. Insere o perfil na tabela public.usuarios
    INSERT INTO public.usuarios (id, usuario, nome_completo, email, tenant_id, is_main_user, direitos, status)
    VALUES (new.id, username_val, full_name_val, new.email, new_tenant_id, TRUE, 'Comum', 'Ativo')
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Habilita a trigger pós insert no auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Notifica o PostgREST para recarregar o schema
NOTIFY pgrst, 'reload schema';
