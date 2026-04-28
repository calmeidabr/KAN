import pandas as pd

def get_from_row(row, key):
    if not row: return None
    import unicodedata
    def remover_acentos(texto):
        if not texto: return ""
        texto_str = str(texto).replace('º', 'o').replace('ª', 'a')
        norm = ''.join(c for c in unicodedata.normalize('NFD', texto_str) if unicodedata.category(c) != 'Mn')
        return norm.encode('latin-1', 'ignore').decode('latin-1')
        
    search_key = remover_acentos(key).lower()
    for k in row.keys():
        if remover_acentos(k).lower() == search_key:
            return row[k]
    return None

df = pd.read_csv("Tabela Matriz.csv", sep=";")
if df.shape[1] <= 1:
    df = pd.read_csv("Tabela Matriz.csv", sep=",")

matriz = {}
for _, row in df.iterrows():
    row_dict = row.to_dict()
    num_val = str(row_dict.get('Resultado', row_dict.get('numero', '')))
    if num_val:
        matriz[num_val] = row_dict

def get_mapped_value(num, campo):
    row = matriz.get(str(num))
    if not row: return "N/A"
    val = get_from_row(row, campo)
    return str(val) if val and pd.notna(val) else "N/A"

print(f"Motivação (7): {get_mapped_value(7, 'Motivação')}")
print(f"Impressão (2): {get_mapped_value(2, 'Impressão')}")
print(f"Expressão (9): {get_mapped_value(9, 'Expressão')}")
print(f"Destino (4): {get_mapped_value(4, 'Destino')}")
print(f"Missão (4): {get_mapped_value(4, 'Missão')}")
print(f"Dia Natalício (22): {get_mapped_value(22, 'Dia Natalício')}")
print(f"Triângulo (9): {get_mapped_value(9, 'Triângulo')}")
print(f"No Psiquico (22): {get_mapped_value(22, 'No Psiquico')}")
print(f"No Psiquico (4): {get_mapped_value(4, 'No Psiquico')}")
print(f"Estrutural (4): {get_mapped_value(4, 'Estrutural')}")
print(f"Direcionamento (2): {get_mapped_value(2, 'Direcionamento')}")
