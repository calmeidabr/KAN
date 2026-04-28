import pandas as pd
import re
import json

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

results = []

def clean_text(s):
    """Limpa espaços e normaliza."""
    return re.sub(r'\s+', ' ', s).strip()

def add_result(categoria, valor, descricao):
    desc = clean_text(descricao)
    if desc:
        results.append({
            "categoria": categoria,
            "valor": str(valor),
            "descricao": desc
        })

# Parser principal com estado
current_section = "Motivacao"
current_num = None
current_desc = ""

def save_current():
    global current_num, current_desc
    if current_num is not None:
        add_result(current_section, current_num, current_desc)
    current_num = None
    current_desc = ""

SIMPLE_HEADERS = {
    "MOTIVAÇÃO": "Motivacao",
    "MOTIVACAO": "Motivacao", 
    "IMPRESSÃO": "Impressao",
    "IMPRESSAO": "Impressao",
    "EXPRESSÃO": "Expressao",
    "EXPRESSAO": "Expressao",
    "DESTINO": "Destino",
    "LIÇÕES CÁRMICAS": "Licao Carmica",
    "TENDÊNCIAS OCULTAS": "Tendencia Oculta",
    "RESPOSTA SUBCONSCIENTE": "Resposta Subconsciente",
    "DÍVIDAS CÁRMICAS": "Divida Carmica",
    "A MISSÃO": "Missao",
    "DIA DO NASCIMENTO": "Dia Natalicio",
    "ANO PESSOAL": "Ano Pessoal",
    "MÊS PESSOAL": "Mes Pessoal",
    "DIA PESSOAL": "Dia Pessoal",
    "CICLOS DE VIDA": "Ciclo de Vida",
}

for i, raw_row in enumerate(rows):
    raw_row = raw_row.strip()
    if not raw_row:
        continue

    # Dividir por \n caso a célula tenha múltiplas linhas
    sub_rows = raw_row.split('\n')
    
    for sub_raw in sub_rows:
        row = sub_raw.strip()
        if not row:
            continue

        upper = row.upper()

        # ── 1. Cabeçalhos de seção simples ──────────────────────────────
        if len(row) < 60:
            matched = None
            for kw, section in SIMPLE_HEADERS.items():
                if upper.startswith(kw):
                    matched = section
                    break
            if matched:
                save_current()
                current_section = matched
                continue

        # ── 2. VIBRAÇÃO «N» → Destino ────────────────────────────────────
        # Match independe de encoding dos guillemets
        m = re.match(r'VIBRA.{1,3}O\s*.(\d+).', upper)
        if m:
            save_current()
            current_section = "Destino"
            current_num = m.group(1)
            current_desc = ""
            continue

        # ── 3. LIÇÃO CÁRMICA N ──────────────────────────────────────────
        m = re.match(r'LI.{1,3}O\s+C.{1,3}RMICA\s+(\d+)', upper)
        if m:
            save_current()
            current_section = "Licao Carmica"
            current_num = m.group(1)
            current_desc = row
            continue

        # ── 4. DÍVIDA CÁRMICA N ─────────────────────────────────────────
        m = re.match(r'D.{1,2}VIDA\s+C.{1,3}RMICA\s*[-–=]?\s*(\d+)', upper)
        if m:
            save_current()
            current_section = "Divida Carmica"
            current_num = m.group(1)
            current_desc = row
            continue

        # ── 5. MISSÃO — N ───────────────────────────────────────────────
        m = re.match(r'MISS.{1,3}O\s*[-–—]\s*(\d+)', upper)
        if m:
            save_current()
            current_section = "Missao"
            current_num = m.group(1)
            current_desc = row
            continue

        # ── 6. DIA NATALÍCIO N ou DATA NATALÍCIA N ──────────────────────
        m = re.match(r'D(?:IA|ATA)\s+NATAL.{1,3}C(?:IO|IA)\s+(\d+)', upper)
        if m:
            save_current()
            current_section = "Dia Natalicio"
            current_num = m.group(1)
            current_desc = row
            continue

        # ── 7. TENDÊNCIA OCULTA N ───────────────────────────────────────
        m = re.match(r'TEND.{1,3}NCIA\s+OCULTA\s+(\d+)', upper)
        if m:
            save_current()
            current_section = "Tendencia Oculta"
            current_num = m.group(1)
            current_desc = row
            continue

        # ── 8. RESPOSTA SUBCONSCIENTE N ─────────────────────────────────
        m = re.match(r'RESPOSTA\s+SUBCONSCIENTE\s+(\d+)', upper)
        if m:
            save_current()
            current_section = "Resposta Subconsciente"
            current_num = m.group(1)
            current_desc = row
            continue

        # ── 9. ANO/MÊS/DIA PESSOAL N ────────────────────────────────────
        m = re.match(r'ANO\s+PESSOAL\s+(\d+)', upper)
        if m:
            save_current()
            current_section = "Ano Pessoal"
            current_num = m.group(1)
            current_desc = row
            continue

        m = re.match(r'M.S\s+PESSOAL\s+(\d+)', upper)
        if m:
            save_current()
            current_section = "Mes Pessoal"
            current_num = m.group(1)
            current_desc = row
            continue

        m = re.match(r'DIA\s+PESSOAL\s+(\d+)', upper)
        if m:
            save_current()
            current_section = "Dia Pessoal"
            current_num = m.group(1)
            current_desc = row
            continue

        # ── 10. Item numerado simples "N - texto" ────────────────────────
        m = re.match(r'^(\d+)\s*[\.\-–]\s*(.+)', row)
        if m and current_section in ["Motivacao", "Impressao", "Expressao"]:
            save_current()
            current_num = m.group(1)
            current_desc = m.group(2)
            continue

        # ── 11. Continuação de texto do item atual ───────────────────────
        if current_num is not None:
            current_desc += " " + row

# Salvar último
save_current()

# Salvar JSON
output_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/clean_mapa_final.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nTotal de itens extraidos: {len(results)}")
stats = {}
for r in results:
    stats[r['categoria']] = stats.get(r['categoria'], 0) + 1
print("\nItens por categoria:")
for cat, count in sorted(stats.items()):
    print(f"  - {cat}: {count}")

# Verificar se Destino e Dia Natalicio foram pegos
if "Destino" not in stats:
    print("\n[AVISO] Destino nao foi detectado!")
if "Dia Natalicio" not in stats:
    print("[AVISO] Dia Natalicio nao foi detectado!")

print(f"\nSalvo em: {output_path}")
