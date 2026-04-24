import pandas as pd
import math

df = pd.read_csv('Desafio.csv', sep=';', encoding='utf-8')

sql = "CREATE TABLE IF NOT EXISTS desafios (dia_nascimento INTEGER PRIMARY KEY, desafio TEXT, descricao TEXT);\n"

for idx, row in df.iterrows():
    try:
        dia = int(row['DIA DO NASCIMENTO'])
        desafio = str(row['DESAFIO']).strip().replace("'", "''")
        descricao = str(row['DESCRICAO']).strip().replace("'", "''")
        
        sql += f"INSERT INTO desafios (dia_nascimento, desafio, descricao) VALUES ({dia}, '{desafio}', '{descricao}');\n"
    except Exception as e:
        print(f"Error on row {idx}: {e}")

with open('desafio.sql', 'w', encoding='utf-8') as f:
    f.write(sql)
print("desafio.sql generated successfully!")
