import pandas as pd
df = pd.read_excel('Tabela Arcanos.xlsx')

sql = 'CREATE TABLE IF NOT EXISTS arcanos (numero INTEGER PRIMARY KEY, nome TEXT, descricao TEXT);\n'

last_numero = None
arcanos_dict = {}

for idx, row in df.iterrows():
    if pd.isna(row['ARCANO']):
        # If no arcano number, it might be an extra description for the last one
        if last_numero is not None:
            extra_desc = str(row['DESCRICAO']).strip()
            if extra_desc and extra_desc != 'nan':
                arcanos_dict[last_numero]['descricao'] += ' ' + extra_desc
        continue
    
    try:
        numero = int(float(row['ARCANO']))
        last_numero = numero
        nome = str(row['NOME']).strip()
        descricao = str(row['DESCRICAO']).strip()
        if nome == 'nan': nome = f'Carta {numero}'
        if descricao == 'nan': descricao = ''
        
        arcanos_dict[numero] = {'nome': nome, 'descricao': descricao}
    except Exception as e:
        continue

for numero, data in arcanos_dict.items():
    nome = data['nome'].replace("'", "''")
    descricao = data['descricao'].replace("'", "''")
    sql += f"INSERT INTO arcanos (numero, nome, descricao) VALUES ({numero}, '{nome}', '{descricao}');\n"

with open('arcanos.sql', 'w', encoding='utf-8') as f:
    f.write(sql)
print("done")
