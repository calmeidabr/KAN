import csv

def clean_sql_string(val):
    if not val:
        return 'NULL'
    val = val.strip().replace("'", "''")
    return f"'{val}'"

try:
    with open('Tabela Matriz.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)
except Exception:
    with open('Tabela Matriz.csv', 'r', encoding='latin-1') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

sql = """
CREATE TABLE IF NOT EXISTS matriz (
    resultado INTEGER PRIMARY KEY,
    motivacao TEXT,
    impressao TEXT,
    expressao TEXT,
    destino TEXT,
    missao TEXT,
    dia_natalicio TEXT,
    talento_oculto TEXT,
    no_psiquico TEXT,
    tendencias_ocultas TEXT,
    resposta_subconsciente TEXT,
    desafios_ciclo TEXT,
    potencialidade_profissional TEXT,
    desafio_aniversario TEXT,
    triangulo TEXT
);

DELETE FROM matriz;
"""

headers = rows[0]
for row in rows[1:]:
    if not row or not row[0].strip():
        continue
    
    # Pad row if it has fewer columns than headers
    while len(row) < len(headers):
        row.append('')
        
    resultado = row[0].strip()
    motivacao = clean_sql_string(row[1])
    impressao = clean_sql_string(row[2])
    expressao = clean_sql_string(row[3])
    destino = clean_sql_string(row[4])
    missao = clean_sql_string(row[5])
    dia_natalicio = clean_sql_string(row[6])
    talento_oculto = clean_sql_string(row[7])
    no_psiquico = clean_sql_string(row[8])
    tendencias_ocultas = clean_sql_string(row[9])
    resposta_subconsciente = clean_sql_string(row[10])
    desafios_ciclo = clean_sql_string(row[11])
    potencialidade_profissional = clean_sql_string(row[12])
    desafio_aniversario = clean_sql_string(row[13])
    triangulo = clean_sql_string(row[14])
    
    sql += f"INSERT INTO matriz (resultado, motivacao, impressao, expressao, destino, missao, dia_natalicio, talento_oculto, no_psiquico, tendencias_ocultas, resposta_subconsciente, desafios_ciclo, potencialidade_profissional, desafio_aniversario, triangulo) VALUES ({resultado}, {motivacao}, {impressao}, {expressao}, {destino}, {missao}, {dia_natalicio}, {talento_oculto}, {no_psiquico}, {tendencias_ocultas}, {resposta_subconsciente}, {desafios_ciclo}, {potencialidade_profissional}, {desafio_aniversario}, {triangulo});\n"

with open('matriz.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("matriz.sql generated successfully!")
