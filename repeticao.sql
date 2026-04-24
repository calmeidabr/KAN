
CREATE TABLE IF NOT EXISTS repeticao (
    repeticao INTEGER PRIMARY KEY,
    perfil TEXT,
    categoria TEXT,
    area_suporte TEXT,
    desafio TEXT
);

DELETE FROM repeticao;
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (1, 'CRIATIVO', 'INOVADOR', NULL, 'INSTALIBIDADE');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (2, NULL, NULL, 'RELACIONAMENTO', 'PASSIVIDADE');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (3, 'COMUNICADOR', NULL, NULL, 'DISPERSÃO');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (4, 'EXECUTOR', 'ORGANIZADO', 'ORGANIZAÇÃO', 'FALTA DE VISÃO');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (5, 'VENDEDOR', 'VERSÁTIL', 'VERSATILIDADE', 'FALTA DE COMPROMETIMENTO');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (6, NULL, NULL, 'SERVIÇO', NULL);
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (7, NULL, 'ANALÍTICO', 'ANÁLISE', 'INSTROSPECÇÃO');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (8, 'LIDER', 'JUSTO', 'JUSTIÇA', 'PREPOTÊNCIA');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (9, 'LIDER', NULL, 'COLETIVIDADE', 'SEM LIMITE');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (11, 'INFLUENCIADOR', NULL, NULL, 'APATIA');
INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES (22, 'RESULTADO', NULL, NULL, 'DÉSPOTA');
