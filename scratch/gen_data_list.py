import pandas as pd
import re

excel_path = "descricao_mapa_numerologico.xlsx"
df = pd.read_excel(excel_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

data_to_insert = []

def clean_desc(d):
    return re.sub(r'\s+', ' ', d).strip()

# --- PRIMEIRO CICLO DE VIDA (Lines 225 to 234) ---
for i in range(225, 235):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+indica\s+(.+)', line)
    if m:
        data_to_insert.append({
            "categoria": "1º Ciclo de Vida",
            "valor": str(m.group(1)),
            "descricao": clean_desc(line)
        })

# --- SEGUNDO CICLO DE VIDA (Lines 237 to 247) ---
for i in range(237, 248):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+(?:mostra|indica|e|nos)\s+(.+)', line)
    if m:
        data_to_insert.append({
            "categoria": "2º Ciclo de Vida",
            "valor": str(m.group(1)),
            "descricao": clean_desc(line)
        })

# --- TERCEIRO CICLO DE VIDA (Lines 250 to 260) ---
for i in range(250, 261):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+(?:indica|mostra|e|nos|talvez)\s+(.+)', line)
    if m:
        data_to_insert.append({
            "categoria": "3º Ciclo de Vida",
            "valor": str(m.group(1)),
            "descricao": clean_desc(line)
        })

# --- DESAFIOS (Lines 262 to 270) ---
for i in range(262, 271):
    line = rows[i].strip()
    m = re.match(r'^Desafio\s+(\d+)\s*[-–]\s*(.+)', line)
    if m:
        data_to_insert.append({
            "categoria": "Desafio",
            "valor": str(m.group(1)),
            "descricao": clean_desc(line)
        })

# --- MOMENTOS DECISIVOS (Lines 278 to 288) ---
for i in range(278, 289):
    line = rows[i].strip()
    m = re.match(r'^MOMENTO\s+DECISIVO\s+(\d+)\s*[-–]\s*(.+)', line)
    if m:
        data_to_insert.append({
            "categoria": "Momento Decisivo",
            "valor": str(m.group(1)),
            "descricao": clean_desc(line)
        })

with open("scratch/data_list.py", "w", encoding="utf-8") as f:
    f.write("REMAINING_DESCRIPTIONS = " + repr(data_to_insert))

print(f"Generated list of dicts with {len(data_to_insert)} items.")
