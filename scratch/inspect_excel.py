import pandas as pd
import re

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)

# Vamos pegar a primeira coluna que parece conter os textos
texts = df.iloc[:, 0].dropna().astype(str).tolist()

sections = {}
current_section = "DESCONHECIDO"

# Padrão para identificar títulos de seção (palavras em maiúsculo sozinhas)
# E padrão para identificar os números (ex: "1 - ", "22 - ")
for line in texts:
    line = line.strip()
    if not line: continue
    
    # Se a linha for apenas uma palavra em maiúsculo (ou poucas), pode ser um título
    if len(line) < 30 and line.isupper():
        current_section = line
        sections[current_section] = []
        continue
    
    # Se começar com número (ex: "1 - ")
    match = re.match(r'^(\d+)\s*[-–]\s*(.*)', line, re.DOTALL)
    if match:
        num = match.group(1)
        content = match.group(2)
        sections.setdefault(current_section, []).append({"numero": num, "texto": content})
    elif current_section in sections and sections[current_section]:
        # Continuação do texto anterior se não começar com número
        sections[current_section][-1]["texto"] += " " + line

# Resumo do que foi encontrado
print(f"Seções detectadas: {list(sections.keys())}")
for sec, items in sections.items():
    print(f"-> {sec}: {len(items)} itens encontrados.")
