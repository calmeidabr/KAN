import os
import sys

sys.path.append(os.getcwd())

from models.database import get_supabase

client = get_supabase()
if not client:
    print('Failed to get Supabase client.')
    sys.exit(1)

try:
    res = client.table('mapas_salvos').select('id, nome').limit(1).execute()
    print('==============================')
    print('Tabela mapas_salvos EXISTE e respondeu com sucesso.')
    print('Dados recebidos:', res.data)
    print('==============================')
except Exception as e:
    print('==============================')
    print('Erro ao acessar mapas_salvos:', str(e))
    print('==============================')
