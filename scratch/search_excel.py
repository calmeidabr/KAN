import pandas as pd

excel_path = "descricao_mapa_numerologico.xlsx"
df = pd.read_excel(excel_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

print("Loaded", len(rows), "rows")

print("\n--- SEARCHING FOR ENTRIES ---")

queries = [
    {"term": "Desafio 4", "label": "1º Desafio 4"},
    {"term": "Desafio 3", "label": "2º Desafio 3"},
    {"term": "Desafio 1", "label": "Desafio Principal 1"},
    {"term": "1º Ciclo de Vida", "label": "1º Ciclo de Vida 7"},
    {"term": "2º Ciclo de Vida", "label": "2º Ciclo de Vida 2"},
    {"term": "3º Ciclo de Vida", "label": "3º Ciclo de Vida 8"},
    {"term": "MOMENTO DECISIVO 9", "label": "1º Momento Decisivo 9"},
    {"term": "MOMENTO DECISIVO 1", "label": "2º Momento Decisivo 1"},
    {"term": "MOMENTO DECISIVO 1", "label": "3º Momento Decisivo 1"},
    {"term": "MOMENTO DECISIVO 6", "label": "4º Momento Decisivo 6"},
]

for q in queries:
    found = False
    for r in rows:
        if q["term"] in r:
            print(f"\n[OK] Found for {q['label']}:")
            print(f"  {r[:150]}...")
            found = True
            break
    if not found:
        print(f"\n[NOT FOUND] {q['label']} (Term: '{q['term']}')")

print("\n--- EXTRACTING RAW BLOCK 220-300 ---")
for i in range(max(0, min(220, len(rows))), min(300, len(rows))):
    print(f"L{i}: {rows[i][:100]}")
