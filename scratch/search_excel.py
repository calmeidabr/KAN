import pandas as pd

excel_path = "descricao_mapa_numerologico.xlsx"
df = pd.read_excel(excel_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

keywords = ["DESAFIO", "CICLO", "MOMENTO"]

print("Searching for keywords in Excel...")
for i, row in enumerate(rows):
    row_upper = row.upper()
    for kw in keywords:
        if kw in row_upper:
            print(f"Line {i} ({kw}): {row[:100]}")
