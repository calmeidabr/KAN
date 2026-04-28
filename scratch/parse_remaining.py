import pandas as pd
import re

excel_path = "descricao_mapa_numerologico.xlsx"
df = pd.read_excel(excel_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

sql_entries = []

# --- PRIMEIRO CICLO DE VIDA (Lines 225 to 234) ---
# Values: 1 to 11
for i in range(225, 235):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+indica\s+(.+)', line)
    if m:
        val = m.group(1)
        desc = line.replace("'", "''")
        sql_entries.append(f"('1o Ciclo de Vida', '{val}', '{desc}')")

# --- SEGUNDO CICLO DE VIDA (Lines 237 to 247) ---
# Values: 1 to 22
for i in range(237, 248):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+(?:mostra|indica|e|nos)\s+(.+)', line)
    if m:
        val = m.group(1)
        desc = line.replace("'", "''")
        sql_entries.append(f"('2o Ciclo de Vida', '{val}', '{desc}')")

# --- TERCEIRO CICLO DE VIDA (Lines 250 to 260) ---
# Values: 1 to 22
for i in range(250, 261):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+(?:indica|mostra|e|nos|talvez)\s+(.+)', line)
    if m:
        val = m.group(1)
        desc = line.replace("'", "''")
        sql_entries.append(f"('3o Ciclo de Vida', '{val}', '{desc}')")

# --- DESAFIOS (Lines 262 to 270) ---
# Values: 0 to 8
for i in range(262, 271):
    line = rows[i].strip()
    m = re.match(r'^Desafio\s+(\d+)\s*[-–]\s*(.+)', line)
    if m:
        val = m.group(1)
        desc = line.replace("'", "''")
        sql_entries.append(f"('Desafio', '{val}', '{desc}')")

# --- MOMENTOS DECISIVOS (Lines 278 to 288) ---
# Values: 1 to 22
for i in range(278, 289):
    line = rows[i].strip()
    m = re.match(r'^MOMENTO\s+DECISIVO\s+(\d+)\s*[-–]\s*(.+)', line)
    if m:
        val = m.group(1)
        desc = line.replace("'", "''")
        sql_entries.append(f"('Momento Decisivo', '{val}', '{desc}')")

# Generate complete SQL
with open("add_remaining_desc.sql", "w", encoding="utf-8") as f:
    f.write("INSERT INTO public.descricoes_mapa (categoria, valor, descricao) VALUES\n")
    f.write(",\n".join(sql_entries))
    f.write("\nON CONFLICT (categoria, valor) DO UPDATE SET descricao = EXCLUDED.descricao;\n")

print(f"Generated SQL with {len(sql_entries)} entries in add_remaining_desc.sql")
