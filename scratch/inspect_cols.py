import pandas as pd

file_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/scratch/temp_excel.xlsx"
df = pd.read_excel(file_path)

# Mostrar as primeiras 30 linhas com todas as colunas preenchidas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 50)

print("Estrutura das Colunas:")
print(df.columns.tolist())

print("\nPrimeiras 30 linhas do arquivo:")
print(df.iloc[0:30, :].to_string())
