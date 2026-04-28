import pandas as pd
import re
import json

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)
texts = df.iloc[:, 0].dropna().astype(str).tolist()

all_data = []
current_field = "MOTIVACAO" # Começa assumindo motivação que é o primeiro do livro

for line in texts:
    line = line.strip()
    if not line: continue
    
    # Detectar Títulos de Seção (Maiúsculas curtas ou palavras chaves)
    # Ignorar se começar com número (pois é item)
    if len(line) < 50 and line.isupper() and not re.match(r'^\d', line):
        current_field = line
        continue

    # Detectar itens numerados: 1-, 1., 1 - , 22 - 
    # Pegar o número e o texto
    match = re.match(r'^(\d+)\s*[\.\-–]\s*(.*)', line, re.DOTALL)
    if match:
        num = match.group(1)
        text = match.group(2)
        all_data.append({
            "campo": current_field.replace("", "A").strip(),
            "numero": num,
            "descricao": text.strip()
        })
    elif all_data and not re.match(r'^[A-Z\s]+$', line):
        # Se for continuação de um texto anterior
        all_data[-1]["descricao"] += " " + line

# Salvar resultado em JSON para conferência
with open("c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/extracted_mapa.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"Total de itens extraídos: {len(all_data)}")
# Mostrar os campos únicos encontrados
campos = sorted(list(set([d['campo'] for d in all_data])))
print(f"Campos identificados: {campos}")
