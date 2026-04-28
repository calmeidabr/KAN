import pandas as pd
import re
import json

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

results = []
current_section = "MOTIVACAO"
current_num = None
current_desc = ""

def save_current():
    global current_num, current_desc, current_section
    if current_num is not None and current_desc.strip():
        # Limpar texto
        text = re.sub(r'\s+', ' ', current_desc).strip()
        results.append({
            "categoria": current_section,
            "valor": str(current_num),
            "descricao": text
        })
        current_desc = ""

# Mapeamento de títulos de seção
section_keywords = {
    "MOTIVAÇÃO": "Motivacao",
    "MOTIVACAO": "Motivacao",
    "IMPRESSÃO": "Impressao",
    "IMPRESSAO": "Impressao",
    "EXPRESSAO": "Expressao",
    "EXPRESSÃO": "Expressao",
    "DESTINO": "Destino",
    "LIÇÕES CÁRMICAS": "Licao Carmica",
    "LICOES CARMICAS": "Licao Carmica",
    "TENDÊNCIAS OCULTAS": "Tendencia Oculta",
    "TENDENCIAS OCULTAS": "Tendencia Oculta",
    "RESPOSTA SUBCONSCIENTE": "Resposta Subconsciente",
    "DÍVIDAS CÁRMICAS": "Divida Carmica",
    "DIVIDAS CARMICAS": "Divida Carmica",
    "A MISSÃO": "Missao",
    "MISSAO": "Missao",
    "DIA NATALÍCIO": "Dia Natalicio",
    "DIA NATALICIO": "Dia Natalicio"
}

for row in rows:
    row_clean = row.strip()
    if not row_clean: continue

    # Verificar se é um cabeçalho de seção
    is_header = False
    for kw, cat in section_keywords.items():
        if kw in row_clean.upper() and len(row_clean) < 50:
            save_current()
            current_section = cat
            current_num = None
            is_header = True
            break
    if is_header: continue

    # Tentar detectar início de item por Regex
    num_match = None
    
    # Caso 1: "1 - " ou "1. "
    m1 = re.match(r'^(\d+)\s*[\.\-–=]\s*(.*)', row_clean)
    if m1:
        num_match = m1.group(1)
        row_clean = m1.group(2)
        
    # Caso 2: "LIÇÃO CÁRMICA 1"
    elif "LIÇÃO CÁRMICA" in row_clean.upper() or "LICAO CARMICA" in row_clean.upper():
        m2 = re.search(r'(\d+)', row_clean)
        if m2: num_match = m2.group(1)
        
    # Caso 3: "DÍVIDA CÁRMICA 13"
    elif "DÍVIDA CÁRMICA" in row_clean.upper() or "DIVIDA CARMICA" in row_clean.upper():
        m3 = re.search(r'(\d+)', row_clean)
        if m3: num_match = m3.group(1)
        
    # Caso 4: "MISSÃO — 1"
    elif "MISSÃO" in row_clean.upper() or "MISSAO" in row_clean.upper():
        m4 = re.search(r'(\d+)', row_clean)
        if m4: num_match = m4.group(1)

    # Caso 5: "DIA NATALÍCIO 1"
    elif "DIA NATALÍCIO" in row_clean.upper() or "DIA NATALICIO" in row_clean.upper():
        m5 = re.search(r'(\d+)', row_clean)
        if m5: num_match = m5.group(1)

    # Se achou um novo número, salva o anterior e começa o novo
    if num_match:
        save_current()
        current_num = num_match
        current_desc = row_clean
    else:
        # Se não achou número, é continuação do texto anterior
        if current_num is not None:
            current_desc += " " + row_clean

# Salva o último
save_current()

# Salva em JSON
with open("c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/clean_mapa.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Sucesso! {len(results)} itens extraídos.")
# Estatísticas
stats = {}
for r in results:
    stats[r['categoria']] = stats.get(r['categoria'], 0) + 1
print("Itens por categoria:")
for cat, count in stats.items():
    print(f" - {cat}: {count}")
