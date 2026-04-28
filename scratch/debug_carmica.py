import pandas as pd
import re

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

print("=== Linhas com CARMICA ou CARMICO ===")
for i, r in enumerate(rows):
    if "CARMICA" in r.upper() or "C\xc1RMICA" in r.upper() or "KARMA" in r.upper() or "C.RMICA" in r.upper():
        print(f"L{i} ({len(r)}): repr={repr(r[:100])}")
