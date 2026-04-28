import urllib.request
import json
import pandas as pd
import re

SUPABASE_URL = "https://wfenlrmsiyndtpxwfgxs.supabase.co"
SUPABASE_KEY = "sb_publishable_c1cNaU04TtPkJ12cZBS0Rw_LvqPs1DQ"

excel_path = "descricao_mapa_numerologico.xlsx"
df = pd.read_excel(excel_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

data_to_insert = []

# Helper to append data safely
def add_entry(cat, val, desc):
    data_to_insert.append({
        "categoria": cat,
        "valor": str(val),
        "descricao": desc.strip()
    })

# --- PRIMEIRO CICLO DE VIDA (Lines 225 to 234) ---
for i in range(225, 235):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+indica\s+(.+)', line)
    if m:
        add_entry("1º Ciclo de Vida", m.group(1), line)

# --- SEGUNDO CICLO DE VIDA (Lines 237 to 247) ---
for i in range(237, 248):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+(?:mostra|indica|e|nos)\s+(.+)', line)
    if m:
        add_entry("2º Ciclo de Vida", m.group(1), line)

# --- TERCEIRO CICLO DE VIDA (Lines 250 to 260) ---
for i in range(250, 261):
    line = rows[i].strip()
    m = re.match(r'^O\s+(\d+)\s*.*?\s+(?:indica|mostra|e|nos|talvez)\s+(.+)', line)
    if m:
        add_entry("3º Ciclo de Vida", m.group(1), line)

# --- DESAFIOS (Lines 262 to 270) ---
for i in range(262, 271):
    line = rows[i].strip()
    m = re.match(r'^Desafio\s+(\d+)\s*[-–]\s*(.+)', line)
    if m:
        add_entry("Desafio", m.group(1), line)

# --- MOMENTOS DECISIVOS (Lines 278 to 288) ---
for i in range(278, 289):
    line = rows[i].strip()
    m = re.match(r'^MOMENTO\s+DECISIVO\s+(\d+)\s*[-–]\s*(.+)', line)
    if m:
        add_entry("Momento Decisivo", m.group(1), line)

# Upsert via REST API
# Using ON CONFLICT header in PostgREST
url = f"{SUPABASE_URL}/rest/v1/descricoes_mapa"
req = urllib.request.Request(url, data=json.dumps(data_to_insert).encode("utf-8"), headers={
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
})

try:
    with urllib.request.urlopen(req) as resp:
        print(f"Success! Status: {resp.status}")
except Exception as e:
    print(f"Error inserting: {e}")
