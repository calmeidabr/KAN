import json

# Lê o JSON gerado
with open("c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/clean_mapa_final.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Gera o arquivo SQL completo
lines = []

# 1. Criar a tabela
lines.append("""-- ============================================================
-- TABELA: descricoes_mapa
-- Armazena as descrições numerológicas extraídas do livro base
-- Execute este script no SQL Editor do Supabase
-- ============================================================

-- Criar a tabela (se não existir)
CREATE TABLE IF NOT EXISTS public.descricoes_mapa (
    id          BIGSERIAL PRIMARY KEY,
    categoria   TEXT NOT NULL,
    valor       TEXT NOT NULL,
    descricao   TEXT NOT NULL,
    UNIQUE (categoria, valor)
);

-- Habilitar RLS (Row Level Security) com política de leitura pública
ALTER TABLE public.descricoes_mapa ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Leitura publica descricoes_mapa"
    ON public.descricoes_mapa
    FOR SELECT USING (true);

-- ============================================================
-- INSERIR OS DADOS (upsert: atualiza se já existir)
-- ============================================================
""")

# 2. Gerar os INSERTs
insert_lines = []
for item in data:
    categoria = item['categoria'].replace("'", "''")
    valor = item['valor'].replace("'", "''")
    descricao = item['descricao'].replace("'", "''")
    insert_lines.append(f"    ('{categoria}', '{valor}', '{descricao}')")

lines.append("INSERT INTO public.descricoes_mapa (categoria, valor, descricao) VALUES")
lines.append(",\n".join(insert_lines))
lines.append("ON CONFLICT (categoria, valor) DO UPDATE SET descricao = EXCLUDED.descricao;")

lines.append(f"""
-- ============================================================
-- VERIFICAÇÃO: Total de registros inseridos
-- ============================================================
SELECT categoria, COUNT(*) as total
FROM public.descricoes_mapa
GROUP BY categoria
ORDER BY categoria;
""")

sql_content = "\n".join(lines)

# Salvar o arquivo SQL
output_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/descricoes_mapa.sql"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(sql_content)

print(f"SQL gerado com {len(data)} registros!")
print(f"Arquivo: {output_path}")
print(f"Tamanho: {len(sql_content):,} bytes")

# Preview das primeiras categorias
cats = {}
for item in data:
    cats[item['categoria']] = cats.get(item['categoria'], 0) + 1
print("\nResumo por categoria:")
for cat, cnt in sorted(cats.items()):
    print(f"  {cat}: {cnt} itens")
