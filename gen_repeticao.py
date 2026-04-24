import csv

def clean_sql_string(val):
    if not val:
        return 'NULL'
    val = val.strip().replace("'", "''")
    return f"'{val}'"

try:
    with open('Repeticao.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)
except Exception:
    with open('Repeticao.csv', 'r', encoding='latin-1') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

sql = """
CREATE TABLE IF NOT EXISTS repeticao (
    repeticao INTEGER PRIMARY KEY,
    perfil TEXT,
    categoria TEXT,
    area_suporte TEXT,
    desafio TEXT
);

DELETE FROM repeticao;
"""

headers = rows[0]
for row in rows[1:]:
    if not row or not row[0].strip():
        continue
    
    while len(row) < 5:
        row.append('')
        
    repeticao = row[0].strip()
    perfil = clean_sql_string(row[1])
    categoria = clean_sql_string(row[2])
    area_suporte = clean_sql_string(row[3])
    desafio = clean_sql_string(row[4])
    
    sql += f"INSERT INTO repeticao (repeticao, perfil, categoria, area_suporte, desafio) VALUES ({repeticao}, {perfil}, {categoria}, {area_suporte}, {desafio});\n"

with open('repeticao.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("repeticao.sql generated successfully!")
