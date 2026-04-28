import os
import pandas as pd

files = [f for f in os.listdir('.') if f.endswith('.csv')]

encodings = ['utf-8', 'latin-1', 'cp1252']

for f in files:
    loaded = False
    for enc in encodings:
        try:
            df = pd.read_csv(f, sep=';', encoding=enc)
            if df.shape[1] <= 1:
                df = pd.read_csv(f, sep=',', encoding=enc)
            
            for col in df.columns:
                for idx, row in df.iterrows():
                    val = str(row[col])
                    if "EXITO" in val.upper() or "ÊXITO" in val.upper():
                        print(f"No arquivo [{f}]: (Encoding: {enc})")
                        print(f"  - Linha {idx+1}, Coluna '{col}' -> '{val}'")
            loaded = True
            break
        except Exception as e:
            continue
    if not loaded:
        print(f"Não foi possível carregar {f}")
