-- Habilita RLS em todas as tabelas
ALTER TABLE arcanos ENABLE ROW LEVEL SECURITY;
ALTER TABLE fortalezas ENABLE ROW LEVEL SECURITY;
ALTER TABLE kans ENABLE ROW LEVEL SECURITY;
ALTER TABLE desafios ENABLE ROW LEVEL SECURITY;
ALTER TABLE matriz ENABLE ROW LEVEL SECURITY;
ALTER TABLE atributos ENABLE ROW LEVEL SECURITY;
ALTER TABLE repeticao ENABLE ROW LEVEL SECURITY;
ALTER TABLE repeticao_descricao ENABLE ROW LEVEL SECURITY;
ALTER TABLE peso ENABLE ROW LEVEL SECURITY;
ALTER TABLE perfis ENABLE ROW LEVEL SECURITY;
ALTER TABLE perfil_descricao ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualidades ENABLE ROW LEVEL SECURITY;
ALTER TABLE lista_categoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE categoria_descricao ENABLE ROW LEVEL SECURITY;
ALTER TABLE peso_categoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE campo_definicao ENABLE ROW LEVEL SECURITY;
ALTER TABLE diferenciais_descricao ENABLE ROW LEVEL SECURITY;
ALTER TABLE descricoes_mapa ENABLE ROW LEVEL SECURITY;
ALTER TABLE kan_banners ENABLE ROW LEVEL SECURITY;
ALTER TABLE kan_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE hierarquia_departamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE mapas_salvos ENABLE ROW LEVEL SECURITY;
ALTER TABLE mapas_salvos_valores ENABLE ROW LEVEL SECURITY;

-- 1. Políticas de Leitura Pública (Acesso Seguro para Anon)
-- Permite que aplicações frontend ou integrações possam APENAS LER os dicionários estáticos.
CREATE POLICY "Permitir leitura publica de dicionarios" ON arcanos FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON fortalezas FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON kans FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON desafios FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON matriz FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON atributos FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON repeticao FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON repeticao_descricao FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON peso FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON perfis FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON perfil_descricao FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON qualidades FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON lista_categoria FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON categoria_descricao FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON peso_categoria FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON campo_definicao FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON diferenciais_descricao FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON descricoes_mapa FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON kan_banners FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON kan_assets FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON empresas FOR SELECT USING (true);
CREATE POLICY "Permitir leitura publica de dicionarios" ON hierarquia_departamentos FOR SELECT USING (true);

-- 2. Políticas para Dados Sensíveis (mapas_salvos, mapas_salvos_valores e usuarios)
-- NENHUMA POLÍTICA CRIADA!
-- Sem políticas de SELECT, INSERT, UPDATE ou DELETE, o acesso para requisições 'anon' 
-- é **totalmente bloqueado** por padrão. Apenas o backend do Streamlit, rodando 
-- de forma invisível e segura com a chave `service_role`, poderá acessar e manipular 
-- esses dados pessoais e as configurações de usuários.
