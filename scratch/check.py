import os
import json
import urllib.request

url = None
key = None
with open('.streamlit/secrets.toml', 'r', encoding='utf-8') as f:
    for line in f:
        if 'SUPABASE_URL' in line:
            url = line.split('=')[1].strip().strip('"').strip("'")
        if 'SUPABASE_KEY' in line:
            key = line.split('=')[1].strip().strip('"').strip("'")

if url and key:
    req = urllib.request.Request(f'{url}/rest/v1/mapas_salvos?select=nome,perfil_json', headers={
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    })
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        print(f'Total profiles: {len(data)}')
        for row in data:
            p = row.get('perfil_json')
            if p and isinstance(p, list):
                for i in p:
                    if isinstance(i, dict) and i.get('Campo') == 'Perfil':
                        print(f"Nome: {row['nome']} | Perfil dict: {i}")
    except Exception as e:
        print(e)
