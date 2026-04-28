import pandas as pd

excel_path = "descricao_mapa_numerologico.xlsx"
df = pd.read_excel(excel_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

for i in range(250, min(320, len(rows))):
    print(f"[{i}]: {rows[i][:120]}")
