import os
import json
import toml
from supabase import create_client

secrets_path = '.streamlit/secrets.toml'
url = None
key = None
try:
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = toml.load(f)
        url = secrets['connections']['supabase']['SUPABASE_URL']
        key = secrets['connections']['supabase']['SUPABASE_KEY']
except Exception as e:
    pass

if url and key:
    supabase = create_client(url, key)
    res = supabase.table('mapas_salvos').select('nome, perfil_json').execute()
    count = 0
    lideres = []
    for row in res.data:
        p_json = row.get('perfil_json')
        if p_json:
            if isinstance(p_json, str):
                try: p_json = json.loads(p_json)
                except: p_json = []
            if isinstance(p_json, list):
                for item in p_json:
                    if isinstance(item, dict) and item.get('Campo') == 'Perfil':
                        if 'Lider' in str(item.get('Valor', '')):
                            count += 1
                            lideres.append(row['nome'])
                            break
    print(f'TOTAL_LIDERES:{count}')
    print('Nomes:', ', '.join(lideres))
else:
    print('No credentials')
