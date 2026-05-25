-- ==========================================
-- SCRIPT: IMPLANTAÇÃO SAAS MULTI-TENANT
-- ==========================================

-- 1. TABELA DE TENANTS (Organizações/Workspaces)
CREATE TABLE IF NOT EXISTS public.tenants (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL,
    slug       TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. TABELA DE PROFILES (Perfil complementar dos usuários)
-- Vinculado diretamente a auth.users gerenciado pelo Supabase Auth
CREATE TABLE IF NOT EXISTS public.profiles (
    id                UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email             TEXT NOT NULL,
    full_name         TEXT,
    default_tenant_id UUID REFERENCES public.tenants(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. TABELA DE ASSOCIAÇÃO (Tenant Members com Roles)
CREATE TABLE IF NOT EXISTS public.tenant_members (
    tenant_id  UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role       TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'member')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tenant_id, user_id)
);

-- 4. TABELA DE NEGÓCIO DE EXEMPLO (cadastros protegidos por RLS)
CREATE TABLE IF NOT EXISTS public.cadastros (
    id         BIGSERIAL PRIMARY KEY,
    tenant_id  UUID REFERENCES public.tenants(id) ON DELETE CASCADE NOT NULL,
    nome       TEXT NOT NULL,
    descricao  TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==========================================
-- CRIAÇÃO DE ÍNDICES PARA POLÍTICAS DE RLS
-- ==========================================
CREATE INDEX IF NOT EXISTS idx_tenant_members_user ON public.tenant_members(user_id);
CREATE INDEX IF NOT EXISTS idx_tenant_members_tenant ON public.tenant_members(tenant_id);
CREATE INDEX IF NOT EXISTS idx_profiles_default_tenant ON public.profiles(default_tenant_id);
CREATE INDEX IF NOT EXISTS idx_cadastros_tenant ON public.cadastros(tenant_id);

-- ==========================================
-- FUNÇÃO AUXILIAR DE SEGURANÇA (SECURITY DEFINER)
-- ==========================================
-- Retorna os IDs dos tenants aos quais o usuário autenticado pertence.
-- SECURITY DEFINER ignora RLS da própria tabela tenant_members para evitar recursão.
CREATE OR REPLACE FUNCTION auth.get_my_tenants()
RETURNS TABLE (tenant_id UUID) 
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT tm.tenant_id 
    FROM public.tenant_members tm
    WHERE tm.user_id = auth.uid();
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- HABILITANDO ROW LEVEL SECURITY (RLS)
-- ==========================================
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cadastros ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- POLÍTICAS RLS: TABELA TENANTS
-- ==========================================
CREATE POLICY "Usuários veem apenas os seus tenants" ON public.tenants
    FOR SELECT TO authenticated
    USING (id IN (SELECT auth.get_my_tenants()));

CREATE POLICY "Dono do tenant pode atualizar detalhes" ON public.tenants
    FOR UPDATE TO authenticated
    USING (id IN (
        SELECT tm.tenant_id FROM public.tenant_members tm 
        WHERE tm.user_id = auth.uid() AND tm.role IN ('owner', 'admin')
    ));

-- ==========================================
-- POLÍTICAS RLS: TABELA PROFILES
-- ==========================================
CREATE POLICY "Usuário vê apenas seu próprio perfil" ON public.profiles
    FOR SELECT TO authenticated
    USING (id = auth.uid());

CREATE POLICY "Usuário pode editar seu próprio perfil" ON public.profiles
    FOR UPDATE TO authenticated
    USING (id = auth.uid());

-- ==========================================
-- POLÍTICAS RLS: TABELA TENANT_MEMBERS
-- ==========================================
CREATE POLICY "Membros veem quem está no mesmo tenant" ON public.tenant_members
    FOR SELECT TO authenticated
    USING (tenant_id IN (SELECT auth.get_my_tenants()));

CREATE POLICY "Owners e Admins gerenciam membros" ON public.tenant_members
    FOR ALL TO authenticated
    USING (tenant_id IN (
        SELECT tm.tenant_id FROM public.tenant_members tm 
        WHERE tm.user_id = auth.uid() AND tm.role IN ('owner', 'admin')
    ));

-- ==========================================
-- POLÍTICAS RLS: TABELA DE NEGÓCIO CADASTROS
-- ==========================================
CREATE POLICY "Membros leem registros do próprio tenant" ON public.cadastros
    FOR SELECT TO authenticated
    USING (tenant_id IN (SELECT auth.get_my_tenants()));

CREATE POLICY "Membros criam registros no próprio tenant" ON public.cadastros
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id IN (SELECT auth.get_my_tenants()));

CREATE POLICY "Membros atualizam registros do próprio tenant" ON public.cadastros
    FOR UPDATE TO authenticated
    USING (tenant_id IN (SELECT auth.get_my_tenants()));

CREATE POLICY "Membros deletam registros do próprio tenant" ON public.cadastros
    FOR DELETE TO authenticated
    USING (tenant_id IN (SELECT auth.get_my_tenants()));

-- ==========================================
-- FLUXO DE ONBOARDING AUTOMÁTICO (TRIGGER)
-- ==========================================
-- Executado sempre que um novo registro entra na tabela auth.users.
-- Cria o tenant básico, o perfil, define como padrão e associa como owner.
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER 
SECURITY DEFINER
AS $$
DECLARE
    new_tenant_id UUID;
    slug_val TEXT;
    full_name_val TEXT;
BEGIN
    -- Cria o slug inicial a partir do e-mail
    slug_val := split_part(new.email, '@', 1) || '-' || floor(random() * 10000)::text;
    full_name_val := coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1));

    -- 1. Insere o Workspace padrão
    INSERT INTO public.tenants (name, slug)
    VALUES (full_name_val || ' Workspace', slug_val)
    RETURNING id INTO new_tenant_id;

    -- 2. Associa o novo usuário ao workspace como owner
    INSERT INTO public.tenant_members (tenant_id, user_id, role)
    VALUES (new_tenant_id, new.id, 'owner');

    -- 3. Insere o perfil estendido
    INSERT INTO public.profiles (id, email, full_name, default_tenant_id)
    VALUES (new.id, new.email, full_name_val, new_tenant_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para automatizar o Onboarding
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
