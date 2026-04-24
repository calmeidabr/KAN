import csv

def clean_sql_string(val):
    if not val:
        return 'NULL'
    val = val.strip().replace("'", "''")
    return f"'{val}'"

try:
    with open('peso.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)
except Exception:
    with open('peso.csv', 'r', encoding='latin-1') as f:
        reader = csv.reader(f, delimiter=';')
        rows = list(reader)

sql = """
CREATE TABLE IF NOT EXISTS peso (
    campo TEXT PRIMARY KEY,
    peso INTEGER
);

DELETE FROM peso;
"""

headers = rows[0]
for row in rows[1:]:
    if not row or not row[0].strip():
        continue
    
    while len(row) < 2:
        row.append('')
        
    campo = clean_sql_string(row[0])
    peso = row[1].strip() if row[1].strip() else '0'
    
    sql += f"INSERT INTO peso (campo, peso) VALUES ({campo}, {peso});\n"

with open('peso.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("peso.sql generated successfully!")
