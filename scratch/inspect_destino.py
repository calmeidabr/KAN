import pandas as pd

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

# Procurar onde aparece a palavra DESTINO
for i, row in enumerate(rows):
    if "DESTINO" in row.upper() and len(row) < 30:
        print(f"\n--- Encontrado DESTINO na linha {i} ---")
        # Mostrar 20 linhas antes e 30 depois
        start = max(0, i - 10)
        end = min(len(rows), i + 40)
        for j in range(start, end):
            print(f"Linha {j}: {rows[j][:100]}")
        break
