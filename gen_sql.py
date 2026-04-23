import pandas as pd
df = pd.read_excel('Tabela Arcanos.xlsx')
print(df.columns)
sql = 'CREATE TABLE IF NOT EXISTS arcanos (numero INTEGER PRIMARY KEY, nome TEXT, descricao TEXT);\n'
for idx, row in df.iterrows():
    numero = row['ARCANO']
    nome = str(row['NOME']).replace("'", "''")
    descricao = str(row['DESCRICAO']).replace("'", "''")
    sql += f"INSERT INTO arcanos (numero, nome, descricao) VALUES ({numero}, '{nome}', '{descricao}');\n"

with open('arcanos.sql', 'w', encoding='utf-8') as f:
    f.write(sql)
print("done")
