-- Criação da tabela de cargos e adição de colunas em mapas_salvos no Supabase

-- 1. Garante as novas colunas de Empresa e Departamento na tabela mapas_salvos
ALTER TABLE mapas_salvos ADD COLUMN IF NOT EXISTS empresa TEXT DEFAULT NULL;
ALTER TABLE mapas_salvos ADD COLUMN IF NOT EXISTS departamento TEXT DEFAULT NULL;

-- 2. Criação da tabela cargos
CREATE TABLE IF NOT EXISTS cargos (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL
);

-- Habilita RLS por padrão para proteger os dados
ALTER TABLE cargos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso total a cargos" ON cargos;
CREATE POLICY "Permitir acesso total a cargos" ON cargos FOR ALL USING (true) WITH CHECK (true);

-- 3. Inserção dos 91 cargos pré-definidos
INSERT INTO cargos (nome) VALUES
('Trainee'),
('Aprendiz'),
('Auxiliar'),
('Assistente'),
('Atendente'),
('Operador'),
('Técnico'),
('Técnico líder'),
('Analista'),
('Analista júnior'),
('Analista pleno'),
('Analista sênior'),
('Especialista'),
('Especialista júnior'),
('Especialista pleno'),
('Especialista sênior'),
('Especialista líder'),
('Especialista principal'),
('Principal'),
('Consultor'),
('Consultor sênior'),
('Consultor estratégico'),
('Assessor'),
('Assessor sênior'),
('Auditor'),
('Perito'),
('Supervisor'),
('Supervisor de equipe'),
('Líder de equipe'),
('Líder de operação'),
('Coordenador'),
('Coordenador sênior'),
('Coordenador regional'),
('Coordenador corporativo'),
('Coordenador de projetos'),
('Encarregado'),
('Chefe de área'),
('Facilitador'),
('Gestão tática'),
('Gerente'),
('Gerente júnior'),
('Gerente pleno'),
('Gerente sênior'),
('Gerente de operações'),
('Gerente de unidade'),
('Gerente regional'),
('Gerente executivo'),
('Head'),
('Head de especialidade'),
('Head de operações'),
('Head de produto'),
('Head de projetos'),
('Diretor adjunto'),
('Diretor'),
('Diretor sênior'),
('Diretor executivo'),
('Diretor-presidente'),
('Vice-presidente'),
('Vice-presidente sênior'),
('Presidente'),
('CEO'),
('COO'),
('CFO'),
('CIO'),
('CTO'),
('CMO'),
('CHRO'),
('CRO'),
('CHO'),
('CPO'),
('Sócio'),
('Sócio fundador'),
('Sócio-diretor'),
('Sócio-administrador'),
('Conselheiro'),
('Membro do conselho'),
('Chairman'),
('Vendedor'),
('Vendedor consultivo'),
('Executivo de vendas'),
('Executivo de contas'),
('Key Account Manager'),
('Account Manager'),
('Pre-sales'),
('Customer Success'),
('Customer Success Manager'),
('Business Development Representative'),
('Sales Development Representative'),
('Closer'),
('Farmer'),
('Hunter')
ON CONFLICT (nome) DO NOTHING;

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';
