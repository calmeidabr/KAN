import pandas as pd
import re
import json

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

results = []

current_section = "Motivacao"
current_num = None
current_desc = ""

def save_current():
    global current_num, current_desc, current_section
    if current_num is not None and current_desc.strip():
        text = re.sub(r'\s+', ' ', current_desc).strip()
        results.append({
            "categoria": current_section,
            "valor": str(current_num),
            "descricao": text
        })
    current_desc = ""
    current_num = None

# Mapeamento de cabeçalhos de seção simples (linha curta em maiúsculo)
SECTION_HEADERS = {
    "MOTIVAÇÃO": "Motivacao",
    "MOTIVACAO": "Motivacao",
    "IMPRESSÃO": "Impressao",
    "IMPRESSAO": "Impressao",
    "EXPRESSÃO": "Expressao",
    "EXPRESSAO": "Expressao",
    "DESTINO": "Destino",
    "LIÇÕES CÁRMICAS": "Licao Carmica",
    "LIÇÕES CARMICAS": "Licao Carmica",
    "LICOES CARMICAS": "Licao Carmica",
    "TENDÊNCIAS OCULTAS": "Tendencia Oculta",
    "TENDENCIAS OCULTAS": "Tendencia Oculta",
    "RESPOSTA SUBCONSCIENTE": "Resposta Subconsciente",
    "DÍVIDAS CÁRMICAS": "Divida Carmica",
    "DIVIDAS CARMICAS": "Divida Carmica",
    "A MISSÃO": "Missao",
    "A MISSAO": "Missao",
    "DIA DO NASCIMENTO": "Dia Natalicio",
    "ANO PESSOAL": "Ano Pessoal",
    "MÊS PESSOAL": "Mes Pessoal",
    "MES PESSOAL": "Mes Pessoal",
    "DIA PESSOAL": "Dia Pessoal",
    "CICLOS DE VIDA": "Ciclo de Vida",
    "PRIMEIRO CICLO DE VIDA": "Primeiro Ciclo de Vida",
    "SEGUNDO CICLO DE VIDA": "Segundo Ciclo de Vida",
    "TERCEIRO CICLO DE VIDA": "Terceiro Ciclo de Vida",
}

def normalize(s):
    """Normaliza string para comparação."""
    return s.strip().upper()

for i, row in enumerate(rows):
    row_clean = row.strip()
    if not row_clean:
        continue

    norm = normalize(row_clean)

    # 1. Verificar se é um cabeçalho de seção simples (linha curta)
    if len(row_clean) < 60:
        matched_section = None
        for kw, section in SECTION_HEADERS.items():
            if norm == kw or norm.startswith(kw + " "):
                matched_section = section
                break
        if matched_section:
            save_current()
            current_section = matched_section
            continue

    # 2. Detectar "VIBRAÇÃO «N»" — indica número do Destino
    m_vibracao = re.match(r'VIBRA[ÇC][ÃA]O\s*[«\"\']?(\d+)[»\"\'»]?', norm)
    if m_vibracao:
        save_current()
        current_num = m_vibracao.group(1)
        # A descrição começa na próxima linha, então deixamos em branco aqui
        current_desc = ""
        continue

    # 3. Detectar "LIÇÃO CÁRMICA N"
    m_licao = re.match(r'LI[ÇC][ÃA]O\s+C[AÁ]RMICA\s+(\d+)', norm)
    if m_licao:
        save_current()
        current_section = "Licao Carmica"
        current_num = m_licao.group(1)
        current_desc = row_clean
        continue

    # 4. Detectar "DÍVIDA CÁRMICA – N" ou "DÍVIDA CÁRMICA N"
    m_divida = re.match(r'D[IÍ]VIDA\s+C[AÁ]RMICA\s*[\-–=]?\s*(\d+)', norm)
    if m_divida:
        save_current()
        current_section = "Divida Carmica"
        current_num = m_divida.group(1)
        current_desc = row_clean
        continue

    # 5. Detectar "MISSÃO — N" ou "MISSÃO – N"
    m_missao = re.match(r'MISS[ÃA]O\s*[\-–—]\s*(\d+)', norm)
    if m_missao:
        save_current()
        current_section = "Missao"
        current_num = m_missao.group(1)
        current_desc = row_clean
        continue

    # 6. Detectar "DIA NATALÍCIO N" ou "DATA NATALÍCIA N"
    m_dia = re.match(r'D(?:IA|ATA)\s+NATAL[IÍ]C[IO|A]\s+(\d+)', norm)
    if m_dia:
        save_current()
        current_section = "Dia Natalicio"
        current_num = m_dia.group(1)
        current_desc = row_clean
        continue

    # 7. Detectar "TENDÊNCIA OCULTA N" ou "RESPOSTA SUBCONSCIENTE N"
    m_tend = re.match(r'TEND[EÊ]NCIA\s+OCULTA\s+(\d+)', norm)
    if m_tend:
        save_current()
        current_section = "Tendencia Oculta"
        current_num = m_tend.group(1)
        current_desc = row_clean
        continue

    m_resp = re.match(r'RESPOSTA\s+SUBCONSCIENTE\s+(\d+)', norm)
    if m_resp:
        save_current()
        current_section = "Resposta Subconsciente"
        current_num = m_resp.group(1)
        current_desc = row_clean
        continue

    # 8. Detectar "ANO PESSOAL N" ou "MÊS PESSOAL N" ou "DIA PESSOAL N"
    m_ano = re.match(r'ANO\s+PESSOAL\s+(\d+)', norm)
    if m_ano:
        save_current()
        current_section = "Ano Pessoal"
        current_num = m_ano.group(1)
        current_desc = row_clean
        continue

    m_mes = re.match(r'M[EÊ]S\s+PESSOAL\s+(\d+)', norm)
    if m_mes:
        save_current()
        current_section = "Mes Pessoal"
        current_num = m_mes.group(1)
        current_desc = row_clean
        continue

    m_diap = re.match(r'DIA\s+PESSOAL\s+(\d+)', norm)
    if m_diap:
        save_current()
        current_section = "Dia Pessoal"
        current_num = m_diap.group(1)
        current_desc = row_clean
        continue

    # 9. Detectar item numerado simples "N - texto" ou "N . texto" (Motivação, Impressão, Expressão)
    m_num = re.match(r'^(\d+)\s*[\.\-–]\s*(.+)', row_clean)
    if m_num and current_section in ["Motivacao", "Impressao", "Expressao"]:
        save_current()
        current_num = m_num.group(1)
        current_desc = m_num.group(2)
        continue

    # 10. Se for continuação de texto do item atual
    if current_num is not None:
        current_desc += " " + row_clean

# Salvar o último item
save_current()

# Salvar JSON
output_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/clean_mapa_v2.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Estatísticas
print(f"\nTotal de itens extraidos: {len(results)}")
stats = {}
for r in results:
    stats[r['categoria']] = stats.get(r['categoria'], 0) + 1
print("\nItens por categoria:")
for cat, count in sorted(stats.items()):
    print(f"  - {cat}: {count}")
print(f"\nSalvo em: {output_path}")
