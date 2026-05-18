-- Tabela Master de Hierarquia e Departamentos das Empresas no Sistema KAN
CREATE TABLE IF NOT EXISTS hierarquia_departamentos (
    id BIGSERIAL PRIMARY KEY,
    empresa TEXT NOT NULL,
    departamento_id TEXT NOT NULL,
    nome TEXT NOT NULL,
    parent_id TEXT,
    ordem INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa, departamento_id)
);

-- Permissões padrão
ALTER TABLE hierarquia_departamentos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso total a hierarquia" ON hierarquia_departamentos;
CREATE POLICY "Permitir acesso total a hierarquia" ON hierarquia_departamentos FOR ALL USING (true) WITH CHECK (true);

-- Notifica o PostgREST para recarregar o schema imediatamente
NOTIFY pgrst, 'reload schema';

-- Inserção de Exemplo Inicial para a Mundo KAN
INSERT INTO hierarquia_departamentos (empresa, departamento_id, nome, parent_id, ordem)
VALUES
('Mundo KAN', 'dept_root', 'Presidência / CEO', NULL, 0),
('Mundo KAN', 'dept_tech', 'Diretoria de Tecnologia', 'dept_root', 1),
('Mundo KAN', 'dept_ops', 'Diretoria de Operações', 'dept_root', 2),
('Mundo KAN', 'dept_dev', 'Desenvolvimento de Software', 'dept_tech', 3),
('Mundo KAN', 'dept_infra', 'Infraestrutura e Nuvem', 'dept_tech', 4),
('Mundo KAN', 'dept_rh', 'Recursos Humanos', 'dept_ops', 5)
ON CONFLICT (empresa, departamento_id) DO NOTHING;
