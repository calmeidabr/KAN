import pandas as pd
import re

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)
rows = df.iloc[:, 0].dropna().astype(str).tolist()

# Mostrar as linhas que contêm VIBRACAO e DIA NATAL
print("=== Linhas com VIBRA ===")
for i, r in enumerate(rows):
    if "VIBRA" in r.upper():
        print(f"L{i}: repr={repr(r[:60])}")

print("\n=== Linhas com DIA NAT ===")
for i, r in enumerate(rows):
    if "DIA NAT" in r.upper() or "DATA NAT" in r.upper():
        print(f"L{i}: repr={repr(r[:80])}")
