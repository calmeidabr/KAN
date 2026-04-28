"""
Teste direto via API REST do Supabase (sem SDK, usa apenas requests).
"""
import urllib.request
import urllib.parse
import json

SUPABASE_URL = "https://wfenlrmsiyndtpxwfgxs.supabase.co"
SUPABASE_KEY = "sb_publishable_c1cNaU04TtPkJ12cZBS0Rw_LvqPs1DQ"

def supabase_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "count=exact"
    })
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        count_range = resp.headers.get("Content-Range", "")
        return json.loads(body), count_range

print("Testando conexao com Supabase...")

# 1. Tentar acessar a tabela descricoes_mapa
try:
    data, count = supabase_get("descricoes_mapa", "select=categoria,valor&limit=200")
    print(f"\nTabela 'descricoes_mapa' - {count}")
    
    stats = {}
    for row in data:
        cat = row["categoria"]
        stats[cat] = stats.get(cat, 0) + 1
    
    print("\nRegistros por categoria:")
    for cat, cnt in sorted(stats.items()):
        print(f"  - {cat}: {cnt}")

    # 2. Amostra
    sample, _ = supabase_get("descricoes_mapa", "select=descricao&categoria=eq.Motivacao&valor=eq.1&limit=1")
    if sample:
        print(f"\nAmostra (Motivacao/1): {sample[0]['descricao'][:80]}...")
    else:
        print("\nTabela existe mas SEM dados ainda! Execute o SQL no Supabase primeiro.")

except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"\nHTTP {e.code}: {body}")
    if e.code == 404:
        print(">> Tabela 'descricoes_mapa' NAO EXISTE ainda. Execute o SQL no Supabase!")
    elif e.code == 401:
        print(">> Chave invalida ou sem permissao.")
except Exception as e:
    print(f"\nErro: {e}")
