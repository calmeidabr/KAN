import csv

def clean_sql_string(val):
    if not val:
        return 'NULL'
    val = val.strip().replace("'", "''")
    return f"'{val}'"

try:
    with open('Atributos.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)
except Exception:
    with open('Atributos.csv', 'r', encoding='latin-1') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

sql = """
CREATE TABLE IF NOT EXISTS atributos (
    atributo TEXT PRIMARY KEY,
    perfil TEXT,
    categoria TEXT,
    area_suporte TEXT
);

DELETE FROM atributos;
"""

headers = rows[0]
for row in rows[1:]:
    if not row or not row[0].strip():
        continue
    
    while len(row) < 4:
        row.append('')
        
    atributo = clean_sql_string(row[0])
    perfil = clean_sql_string(row[1])
    categoria = clean_sql_string(row[2])
    area_suporte = clean_sql_string(row[3])
    
    sql += f"INSERT INTO atributos (atributo, perfil, categoria, area_suporte) VALUES ({atributo}, {perfil}, {categoria}, {area_suporte});\n"

with open('atributos.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("atributos.sql generated successfully!")
