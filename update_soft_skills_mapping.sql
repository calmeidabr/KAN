-- Adiciona as novas colunas
ALTER TABLE soft_skills ADD COLUMN IF NOT EXISTS perfis_relacionados TEXT;
ALTER TABLE soft_skills ADD COLUMN IF NOT EXISTS categorias_relacionadas TEXT;
ALTER TABLE soft_skills ADD COLUMN IF NOT EXISTS qualidades_relacionadas TEXT;

-- Atualiza cada linha com a análise comportamental
UPDATE soft_skills SET perfis_relacionados = 'Comunicador, Lider', categorias_relacionadas = 'Comunicativo, Diplomático', qualidades_relacionadas = 'Comunicação, Relacionamento' WHERE nome = 'Comunicação eficaz';
UPDATE soft_skills SET perfis_relacionados = 'Lider, Comunicador', categorias_relacionadas = 'Justo, Comunicativo', qualidades_relacionadas = 'Comunicação, Justiça' WHERE nome = 'Comunicação assertiva';
UPDATE soft_skills SET perfis_relacionados = 'Comunicador, Influenciador', categorias_relacionadas = 'Diplomático, Harmônico', qualidades_relacionadas = 'Comunicação, Relacionamento' WHERE nome = 'Escuta ativa';
UPDATE soft_skills SET perfis_relacionados = 'Influenciador, Executor', categorias_relacionadas = 'Harmônico, Versátil', qualidades_relacionadas = 'Coletividade, Relacionamento' WHERE nome = 'Trabalho em equipe';
UPDATE soft_skills SET perfis_relacionados = 'Influenciador, Comunicador', categorias_relacionadas = 'Diplomático, Harmônico', qualidades_relacionadas = 'Relacionamento, Coletividade' WHERE nome = 'Relacionamento interpessoal';
UPDATE soft_skills SET perfis_relacionados = 'Influenciador, Lider', categorias_relacionadas = 'Intuitivo, Harmônico', qualidades_relacionadas = 'Intuição, Relacionamento' WHERE nome = 'Empatia';
UPDATE soft_skills SET perfis_relacionados = 'Executor, Resultado', categorias_relacionadas = 'Harmônico, Realizador', qualidades_relacionadas = 'Coletividade, Serviço' WHERE nome = 'Colaboração';
UPDATE soft_skills SET perfis_relacionados = 'Lider, Resultado', categorias_relacionadas = 'Visionário, Realizador', qualidades_relacionadas = 'Execução, Coletividade' WHERE nome = 'Liderança';
UPDATE soft_skills SET perfis_relacionados = 'Lider, Influenciador', categorias_relacionadas = 'Intuitivo, Diplomático', qualidades_relacionadas = 'Intuição, Relacionamento' WHERE nome = 'Inteligência emocional';
UPDATE soft_skills SET perfis_relacionados = 'Executor, Resultado', categorias_relacionadas = 'Realizador, Versátil', qualidades_relacionadas = 'Execução, Praticidade e Disciplina' WHERE nome = 'Resiliência';
UPDATE soft_skills SET perfis_relacionados = 'Criativo, Vendedor', categorias_relacionadas = 'Versátil, Inovador', qualidades_relacionadas = 'Versatilidade, Intuição' WHERE nome = 'Adaptabilidade / flexibilidade';
UPDATE soft_skills SET perfis_relacionados = 'Executor, Resultado', categorias_relacionadas = 'Realizador, Visionário', qualidades_relacionadas = 'Execução, Praticidade e Disciplina' WHERE nome = 'Proatividade';
UPDATE soft_skills SET perfis_relacionados = 'Executor', categorias_relacionadas = 'Organizado, Analítico', qualidades_relacionadas = 'Organização, Praticidade e Disciplina' WHERE nome = 'Organização';
UPDATE soft_skills SET perfis_relacionados = 'Resultado, Executor', categorias_relacionadas = 'Organizado, Realizador', qualidades_relacionadas = 'Organização, Praticidade e Disciplina' WHERE nome = 'Gestão do tempo';
UPDATE soft_skills SET perfis_relacionados = 'Executor, Resultado', categorias_relacionadas = 'Organizado, Realizador', qualidades_relacionadas = 'Praticidade e Disciplina, Execução' WHERE nome = 'Disciplina';
UPDATE soft_skills SET perfis_relacionados = 'Executor', categorias_relacionadas = 'Organizado, Justo', qualidades_relacionadas = 'Praticidade e Disciplina, Organização' WHERE nome = 'Pontualidade';
UPDATE soft_skills SET perfis_relacionados = 'Resultado, Executor', categorias_relacionadas = 'Analítico, Organizado', qualidades_relacionadas = 'Análise, Organização' WHERE nome = 'Atenção / foco';
UPDATE soft_skills SET perfis_relacionados = 'Criativo, Lider', categorias_relacionadas = 'Analítico, Visionário', qualidades_relacionadas = 'Análise, Intuição' WHERE nome = 'Pensamento crítico';
UPDATE soft_skills SET perfis_relacionados = 'Criativo, Resultado', categorias_relacionadas = 'Analítico, Realizador', qualidades_relacionadas = 'Execução, Análise' WHERE nome = 'Resolução de problemas';
UPDATE soft_skills SET perfis_relacionados = 'Lider, Resultado', categorias_relacionadas = 'Justo, Visionário', qualidades_relacionadas = 'Execução, Análise' WHERE nome = 'Tomada de decisão';
UPDATE soft_skills SET perfis_relacionados = 'Criativo, Vendedor', categorias_relacionadas = 'Inovador, Visionário', qualidades_relacionadas = 'Intuição, Versatilidade' WHERE nome = 'Criatividade';
UPDATE soft_skills SET perfis_relacionados = 'Criativo, Lider', categorias_relacionadas = 'Inovador, Visionário', qualidades_relacionadas = 'Execução, Intuição' WHERE nome = 'Inovação / melhoria contínua';
UPDATE soft_skills SET perfis_relacionados = 'Lider, Resultado', categorias_relacionadas = 'Visionário, Analítico', qualidades_relacionadas = 'Análise, Coletividade' WHERE nome = 'Visão sistêmica';
UPDATE soft_skills SET perfis_relacionados = 'Lider, Executor', categorias_relacionadas = 'Justo, Harmônico', qualidades_relacionadas = 'Justiça, Coletividade' WHERE nome = 'Ética / responsabilidade';
UPDATE soft_skills SET perfis_relacionados = 'Resultado, Executor', categorias_relacionadas = 'Realizador, Organizado', qualidades_relacionadas = 'Execução, Praticidade e Disciplina' WHERE nome = 'Produtividade';
UPDATE soft_skills SET perfis_relacionados = 'Criativo, Resultado', categorias_relacionadas = 'Conhecimento, Inovador', qualidades_relacionadas = 'Versatilidade, Análise' WHERE nome = 'Aprendizado contínuo';
