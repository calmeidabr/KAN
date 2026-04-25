
-- Tabela lista_categoria
CREATE TABLE IF NOT EXISTS lista_categoria (
    id SERIAL PRIMARY KEY,
    categoria TEXT
);

INSERT INTO lista_categoria (categoria) VALUES
('Justo'), ('Inovador'), ('Diplomático'), ('Realizador'), ('Versátil'),
('Visionário'), ('Magnético'), ('Analítico'), ('Organizado'), ('Harmônico'),
('Comunicativo'), ('Intuitivo'), ('Conhecimento');

-- Tabela peso_categoria
CREATE TABLE IF NOT EXISTS peso_categoria (
    id SERIAL PRIMARY KEY,
    peso INTEGER,
    campo TEXT
);

INSERT INTO peso_categoria (peso, campo) VALUES
(100, 'Motivação'), (100, 'Impressão'), (100, 'Expressão'), (100, 'Destino'),
(100, 'Missão'), (150, 'Dia Natalício'), (100, 'Triângulo'), (100, 'No Psiquico'),
(100, 'Estrutural'), (100, 'Direcionamento'), (100, 'REPETIÇÃO 1'), (100, 'REPETIÇÃO 2');
