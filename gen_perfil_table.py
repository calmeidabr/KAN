import csv

def clean_sql_string(val):
    if not val:
        return 'NULL'
    val = val.strip().replace("'", "''")
    return f"'{val}'"

try:
    with open('perfil.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)
except Exception:
    with open('perfil.csv', 'r', encoding='latin-1') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

sql = """
CREATE TABLE IF NOT EXISTS perfis (
    perfil TEXT PRIMARY KEY
);

DELETE FROM perfis;
"""

headers = rows[0]
for row in rows[1:]:
    if not row or not row[0].strip():
        continue
    
    perfil = clean_sql_string(row[0])
    
    sql += f"INSERT INTO perfis (perfil) VALUES ({perfil});\n"

with open('perfil.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("perfil.sql generated successfully!")
